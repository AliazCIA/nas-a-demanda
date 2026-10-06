---
name: dev-operacion
description: Cómo probar, instalar y verificar privacidad en nas-a-demanda sin tocar una instalación real.
metadata:
  type: project
---

# Operación del repo

**Probar sin tocar una instalación real:**
- Panel: `python3 -m unittest discover -s tests -v` — levanta el Panel en un puerto libre contra un `~/nas`
  falso (`NAS_DIR` a un temporal) y sustituye `run` (no llama a systemctl ni virsh de verdad).
- Plantillas del Tablero: extrae el bloque python de `instalar.sh` y córrelo contra una copia en un
  directorio temporal con `.env` de ejemplo; valida que no queden `${...}` y que los YAML carguen.
- `bash -n instalar.sh bin/*.sh scripts/*.sh`.
- ❌ NO corras `instalar.sh` en una máquina con instalación viva para "probar": re-enlaza quadlets y reinicia servicios.

**Privacidad antes de commitear (repo público):**
- `scripts/verificar-sin-datos-personales.sh --instalar` una vez por clon (pre-commit).
- Capa 2 = `privado/patrones-personales.txt` (local, gitignoreado): una regex por renglón con la IP, la red
  Tailscale, usuarios, nombre del disco, VM y las CLAVES reales de `.env`. Sin ese archivo solo corre la capa 1.

**Instalación viva vs repo:** el repo se clona en `~/nas`; `.env`, `tablero.env`, `appdata/` y `datos` quedan
fuera de git, así un clon ES la instalación. Las plantillas del Tablero se copian a `appdata/` una sola vez:
cambios posteriores a `plantillas/` no tocan un Tablero ya instalado.
