"""Pruebas del Panel: que deje entrar solo con la clave correcta, que no encienda sin disco
y que encienda/apague los servicios en el orden correcto. Corre con: python3 -m unittest -v"""
import base64
import importlib
import json
import os
import sys
import tempfile
import threading
import unittest
import urllib.request
from pathlib import Path
from urllib.error import HTTPError

RAIZ = Path(__file__).resolve().parent.parent


def cargar_panel(env_texto):
    """Importa panel.py contra un ~/nas falso con el .env dado (la config se lee al importar)."""
    tmp = tempfile.mkdtemp()
    Path(tmp, ".env").write_text(env_texto)
    os.environ["NAS_DIR"] = tmp
    sys.path.insert(0, str(RAIZ / "panel"))
    sys.modules.pop("panel", None)
    return importlib.import_module("panel")


ENV = "PANEL_USUARIO=admin\nPANEL_PASSWORD=secreta\nNAS_IP=192.0.2.10\nDISCO_NOMBRE=PRUEBA\nVM_NOMBRE=\n"


class PanelHTTP(unittest.TestCase):
    def setUp(self):
        self.panel = cargar_panel(ENV)
        self.llamadas = []

        class R:  # resultado falso de subprocess.run
            returncode, stdout, stderr = 0, "inactive", ""

        self.panel.run = lambda cmd: (self.llamadas.append(cmd), R())[1]
        self.srv = self.panel.ThreadingHTTPServer(("127.0.0.1", 0), self.panel.Handler)
        threading.Thread(target=self.srv.serve_forever, daemon=True).start()
        self.base = f"http://127.0.0.1:{self.srv.server_address[1]}"

    def tearDown(self):
        self.srv.shutdown()
        self.srv.server_close()

    def pedir(self, ruta, metodo="GET", usuario=None, clave=None, x_panel=True):
        req = urllib.request.Request(self.base + ruta, method=metodo, data=b"" if metodo == "POST" else None)
        if usuario is not None:
            req.add_header("Authorization", "Basic " + base64.b64encode(f"{usuario}:{clave}".encode()).decode())
        if x_panel:
            req.add_header("X-Panel", "1")
        try:
            with urllib.request.urlopen(req) as r:
                return r.status, r.read()
        except HTTPError as e:
            with e:
                return e.code, e.read()

    def test_salud_responde_sin_login(self):
        self.assertEqual(self.pedir("/salud"), (200, b"ok"))

    def test_sin_vm_configurada_salud_vm_es_503(self):
        self.assertEqual(self.pedir("/salud/vm")[0], 503)

    def test_rechaza_sin_clave_y_con_clave_mala(self):
        self.assertEqual(self.pedir("/api/estado")[0], 401)
        self.assertEqual(self.pedir("/api/estado", usuario="admin", clave="mala")[0], 401)
        self.assertEqual(self.pedir("/api/estado", usuario="otro", clave="secreta")[0], 401)

    def test_acepta_la_clave_correcta_y_no_muestra_la_vm_si_no_hay(self):
        code, cuerpo = self.pedir("/api/estado", usuario="admin", clave="secreta")
        self.assertEqual(code, 200)
        e = json.loads(cuerpo)
        self.assertEqual(e["disco_nombre"], "PRUEBA")
        self.assertNotIn("vm", [g["clave"] for g in e["grupos"]])

    def test_post_sin_encabezado_x_panel_se_rechaza(self):
        code, _ = self.pedir("/api/immich/encender", "POST", "admin", "secreta", x_panel=False)
        self.assertEqual(code, 403)
        self.assertEqual(self.llamadas, [])

    def test_no_enciende_sin_disco(self):
        self.panel.disco_montado = lambda: False
        code, cuerpo = self.pedir("/api/immich/encender", "POST", "admin", "secreta")
        self.assertEqual(code, 409)
        self.assertIn("PRUEBA", json.loads(cuerpo)["error"])
        self.assertFalse([c for c in self.llamadas if "start" in c])

    def test_enciende_en_orden_y_apaga_al_reves(self):
        self.panel.disco_montado = lambda: True
        self.assertEqual(self.pedir("/api/immich/encender", "POST", "admin", "secreta")[0], 200)
        self.assertEqual(self.pedir("/api/immich/apagar", "POST", "admin", "secreta")[0], 200)
        units = ["immich-postgres", "immich-redis", "immich-ml", "immich-server"]
        start = next(c for c in self.llamadas if "start" in c)
        stop = next(c for c in self.llamadas if "stop" in c)
        self.assertEqual(start[-4:], units)
        self.assertEqual(stop[-4:], units[::-1])

    def test_servicio_inexistente_es_404(self):
        self.assertEqual(self.pedir("/api/nada/encender", "POST", "admin", "secreta")[0], 404)


class ClaveVacia(unittest.TestCase):
    def test_sin_clave_configurada_nadie_entra(self):
        panel = cargar_panel("PANEL_USUARIO=admin\nPANEL_PASSWORD=\n")

        class H:
            headers = {"Authorization": "Basic " + base64.b64encode(b"admin:").decode()}

        self.assertFalse(panel.Handler.autorizado(H()))


class ConVM(unittest.TestCase):
    def test_con_vm_aparecen_vm_y_portal(self):
        panel = cargar_panel(ENV.replace("VM_NOMBRE=", "VM_NOMBRE=win\nVM_IP=192.0.2.20"))
        self.assertIn("vm", panel.GRUPOS)
        self.assertEqual(panel.GRUPOS["guacamole"]["units"], ["nas-guacd", "nas-guacamole"])
        self.assertEqual(panel.VM_RDP, ("192.0.2.20", 3389))


if __name__ == "__main__":
    unittest.main()
