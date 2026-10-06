#!/usr/bin/env bash
# Instala/actualiza el NAS en ESTA máquina. Idempotente: se puede correr las veces que sea.
# El repo debe vivir en ~/nas (los quadlets usan %h/nas). Requisitos y pasos: README.md.
set -euo pipefail
N="$(cd "$(dirname "$0")" && pwd)"
[[ "$N" == "$HOME/nas" ]] || { echo "✖ Clona el repo en ~/nas (está en $N)." >&2; exit 1; }
for c in podman systemctl python3; do
    command -v "$c" >/dev/null || { echo "✖ Falta $c." >&2; exit 1; }
done

# 1) Secretos: se crean desde los ejemplos y se detiene para que los llenes.
falta=0
for f in .env tablero.env; do
    if [[ ! -f "$N/$f" ]]; then
        cp "$N/$f.example" "$N/$f"; chmod 600 "$N/$f"
        echo "→ Creé $f desde $f.example: llénalo."; falta=1
    fi
done
if [[ ! -e "$N/appdata/samba/samba.env" ]]; then
    mkdir -p "$N/appdata/samba"
    cp "$N/plantillas/samba/samba.env.example" "$N/appdata/samba/samba.env"; chmod 600 "$N/appdata/samba/samba.env"
    echo "→ Creé appdata/samba/samba.env: pon tu usuario y clave de Samba."; falta=1
fi
[[ $falta -eq 0 ]] || { echo "Vuelve a correr ./instalar.sh cuando termines de editarlos."; exit 0; }

# 2) Disco de datos: ~/nas/datos debe apuntar a la carpeta del disco externo.
if [[ ! -L "$N/datos" ]]; then
    echo "⚠ Falta el enlace al disco: ln -sfn /ruta/al/disco/NAS ~/nas/datos (los servicios que lo usan no encenderán sin él)."
fi

# 3) appdata: configuración y bases de datos, SIEMPRE en el disco del sistema (Linux), nunca en el externo.
mkdir -p "$N"/appdata/{homepage,filebrowser,immich/postgres,syncthing,guacamole}
[[ -f "$N/appdata/filebrowser/config.yaml" ]] || cp "$N/plantillas/filebrowser/config.yaml" "$N/appdata/filebrowser/"

# Las plantillas del Tablero se copian UNA vez, llenando ${VARIABLES} con .env; después el Tablero es tuyo.
python3 - "$N" <<'EOF'
import re, sys
from pathlib import Path
n = Path(sys.argv[1])
env = dict(l.split("=", 1) for l in (n / ".env").read_text().splitlines() if "=" in l and not l.startswith("#"))
destino = n / "appdata/homepage"
for p in (n / "plantillas/homepage").iterdir():
    d = destino / p.name
    if d.exists():
        continue
    d.write_text(re.sub(r"\$\{([A-Z_]+)\}", lambda m: env.get(m.group(1), m.group(0)), p.read_text()))
    print(f"→ Tablero: creé {d.relative_to(n)}")
vm = env.get("VM_NOMBRE", "").strip()
g = n / "appdata/guacamole/user-mapping.xml"
if vm and not g.exists():
    g.write_text((n / "plantillas/guacamole/user-mapping.xml.example").read_text())
    g.chmod(0o600)
    print("→ Creé appdata/guacamole/user-mapping.xml: pon tu usuario, clave (MD5) y la IP de la VM.")
EOF

# 4) Enlaza los quadlets y servicios de usuario (editar el repo = editar el sistema).
D="$HOME/.config/containers/systemd"; U="$HOME/.config/systemd/user"
mkdir -p "$D" "$U"
for f in "$N"/stack/*; do ln -sfn "$f" "$D/$(basename "$f")"; done
for f in "$N"/systemd/*; do ln -sfn "$f" "$U/$(basename "$f")"; done

loginctl enable-linger "$USER" 2>/dev/null || true
systemctl --user daemon-reload
# Con la PC solo arrancan el Tablero (:3000) y el Panel (:3001); lo demás se enciende desde el Panel.
systemctl --user enable --now nas-panel.service organizar-fotos.timer
systemctl --user start nas-tablero.service
IP="$(grep -m1 '^NAS_IP=' "$N/.env" | cut -d= -f2-)"
echo "✔ Listo. Tablero: http://$IP:3000 · Panel: http://$IP:3001 (claves: ~/nas/bin/claves.sh)"
