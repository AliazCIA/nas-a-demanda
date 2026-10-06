#!/usr/bin/env python3
"""Panel de encendido del NAS: enciende/apaga a demanda cada servicio y la VM.

Arranca con la PC (junto al Tablero); todo lo demás NO arranca solo — ver DECISIONES.md.
Solo librería estándar. Toda la configuración sale de ~/nas/.env (ver .env.example).
"""
import base64
import hmac
import json
import os
import shutil
import socket
import subprocess
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HOME = Path.home()
NAS = Path(os.environ.get("NAS_DIR", HOME / "nas"))
DATOS = NAS / "datos"
VIRSH = ["virsh", "-c", "qemu:///system"]


def cargar_env():
    env = {}
    archivo = NAS / ".env"
    if archivo.exists():
        for linea in archivo.read_text().splitlines():
            if "=" in linea and not linea.lstrip().startswith("#"):
                k, v = linea.split("=", 1)
                env[k.strip()] = v.strip()
    return env


CONF = cargar_env()
PUERTO = int(CONF.get("PANEL_PUERTO", "3001"))
NAS_IP = CONF.get("NAS_IP", "<ip-del-nas>")
DISCO = CONF.get("DISCO_NOMBRE", "de datos")
VM = CONF.get("VM_NOMBRE", "")
VM_RDP = (CONF.get("VM_IP", ""), 3389)

# Orden = orden de arranque; se apagan al revés. "disco": no se enciende sin el disco de datos.
GRUPOS = {
    "immich": {"nombre": "Immich", "para": "Fotos y videos del celular", "disco": True,
               "url": ":2283", "units": ["immich-postgres", "immich-redis", "immich-ml", "immich-server"]},
    "syncthing": {"nombre": "Syncthing", "para": "Respaldo continuo de celulares y laptops", "disco": True,
                  "url": ":8384", "units": ["nas-syncthing"]},
    "archivos": {"nombre": "Archivos", "para": "Explorador de archivos del NAS", "disco": True,
                 "url": ":8081", "units": ["nas-archivos"]},
    "samba": {"nombre": "Carpetas de red (Samba)", "para": f"\\\\{NAS_IP} desde Windows/celular", "disco": True,
              "url": None, "units": ["nas-samba"]},
}
if VM:  # la VM y su portal web solo existen si .env define VM_NOMBRE
    GRUPOS["vm"] = {"nombre": "Windows (VM)", "para": f"Entrar por RDP a {NAS_IP}", "disco": False,
                    "url": None, "units": []}
    GRUPOS["guacamole"] = {"nombre": "Portal web de la VM", "para": "Guacamole, respaldo del RDP", "disco": False,
                           "url": ":8080/guacamole", "units": ["nas-guacd", "nas-guacamole"]}


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, timeout=30)


def disco_montado():
    """El disco está si ~/nas/datos resuelve a un directorio de OTRO sistema de archivos que $HOME.

    Sin esto, un servicio arrancado sin disco escribiría en el disco del sistema (o fallaría en silencio).
    """
    real = DATOS.resolve()
    try:
        return real.is_dir() and os.stat(real).st_dev != os.stat(HOME).st_dev
    except OSError:
        return False


def estado_units(units):
    activos = [run(["systemctl", "--user", "is-active", u]).stdout.strip() for u in units]
    if all(a == "active" for a in activos):
        return "encendido"
    if any(a in ("activating", "deactivating", "reloading") for a in activos):
        return "cambiando"
    if any(a == "active" for a in activos):
        return "a medias"
    if any(a == "failed" for a in activos):
        return "falló"
    return "apagado"


def estado_vm():
    s = run(VIRSH + ["domstate", VM]).stdout.strip()
    return {"ejecutando": "encendido", "apagado": "apagado", "running": "encendido",
            "shut off": "apagado"}.get(s, s or "desconocido")


def vm_lista_para_rdp():
    """Encendida no basta: Windows tarda en arrancar; solo cuenta si su RDP ya acepta conexiones."""
    if not VM or estado_vm() != "encendido":
        return False
    try:
        with socket.create_connection(VM_RDP, timeout=2):
            return True
    except OSError:
        return False


def estado():
    disco = disco_montado()
    uso = None
    if disco:
        u = shutil.disk_usage(DATOS.resolve())
        uso = {"total_gb": round(u.total / 1e9), "libre_gb": round(u.free / 1e9)}
    grupos = []
    for clave, g in GRUPOS.items():
        est = estado_vm() if clave == "vm" else estado_units(g["units"])
        grupos.append({"clave": clave, "nombre": g["nombre"], "para": g["para"], "estado": est,
                       "url": g["url"], "necesita_disco": g["disco"]})
    return {"disco": disco, "disco_nombre": DISCO, "uso": uso, "grupos": grupos}


def accion(clave, que):
    g = GRUPOS.get(clave)
    if g is None or que not in ("encender", "apagar"):
        return 404, {"error": "no existe"}
    if que == "encender" and g["disco"] and not disco_montado():
        return 409, {"error": f"El disco {DISCO} no está conectado: conéctalo y vuelve a intentar."}
    if clave == "vm":
        r = run(VIRSH + (["start", VM] if que == "encender" else ["shutdown", VM]))
    elif que == "encender":
        r = run(["systemctl", "--user", "reset-failed", *g["units"]])
        r = run(["systemctl", "--user", "start", "--no-block", *g["units"]])
    else:
        r = run(["systemctl", "--user", "stop", "--no-block", *reversed(g["units"])])
    if r.returncode != 0:
        return 500, {"error": (r.stderr or r.stdout).strip()}
    return 200, {"ok": True}


PAGINA = (Path(__file__).parent / "index.html").read_bytes()


class Handler(BaseHTTPRequestHandler):
    def autorizado(self):
        h = self.headers.get("Authorization", "")
        if not h.startswith("Basic "):
            return False
        try:
            user, _, pw = base64.b64decode(h[6:]).decode().partition(":")
        except Exception:
            return False
        env = cargar_env()  # se relee: cambiar la clave en .env no exige reiniciar el Panel
        return (hmac.compare_digest(user, env.get("PANEL_USUARIO", "")) and
                hmac.compare_digest(pw, env.get("PANEL_PASSWORD", "")) and pw != "")

    def responder(self, code, cuerpo, tipo="application/json"):
        data = cuerpo if isinstance(cuerpo, bytes) else json.dumps(cuerpo).encode()
        self.send_response(code)
        self.send_header("Content-Type", tipo)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def exigir_login(self):
        if self.autorizado():
            return True
        self.send_response(401)
        self.send_header("WWW-Authenticate", 'Basic realm="Panel del NAS", charset="UTF-8"')
        self.send_header("Content-Length", "0")
        self.end_headers()
        return False

    def do_GET(self):
        if self.path == "/salud":  # sin login: solo para el monitor del Tablero, no revela nada
            self.responder(200, b"ok", "text/plain")
            return
        if self.path == "/salud/vm":  # sin login: 200 = la VM acepta RDP, 503 = no
            lista = vm_lista_para_rdp()
            self.responder(200 if lista else 503, b"lista" if lista else b"no disponible", "text/plain")
            return
        if not self.exigir_login():
            return
        if self.path == "/":
            self.responder(200, PAGINA, "text/html; charset=utf-8")
        elif self.path == "/api/estado":
            self.responder(200, estado())
        else:
            self.responder(404, {"error": "no existe"})

    def do_POST(self):
        if not self.exigir_login():
            return
        # Un formulario de otro sitio no puede mandar este encabezado (CSRF).
        if self.headers.get("X-Panel") != "1":
            self.responder(403, {"error": "falta X-Panel"})
            return
        partes = self.path.strip("/").split("/")
        if len(partes) != 3 or partes[0] != "api":
            self.responder(404, {"error": "no existe"})
            return
        self.responder(*accion(partes[1], partes[2]))

    def log_message(self, fmt, *args):
        pass


if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", PUERTO), Handler).serve_forever()
