# AGENTS.md — Reglas del repo nas-a-demanda

> Ley del repo. Si una idea nueva contradice algo de aquí, se discute con el dueño ANTES de hacerla.
> Porqués y contexto: [DECISIONES.md](DECISIONES.md).

## §1 Stack fijo
- **podman rootless + quadlets** (`stack/*.container`), como el usuario normal. Nada de Docker Compose ni root.
- **Panel:** Python 3, **solo librería estándar** (`http.server`). Sin pip, sin frameworks.
- **Tablero:** Homepage en contenedor; su config inicial vive en `plantillas/homepage/`.
- Servicios que no son contenedores → `systemd/` (de usuario) o `sistema/` (de sistema, solo si exige privilegio).

## §2 Arranque a demanda (inviolable)
- Con la PC arrancan **solo** el Tablero y el Panel. Un servicio nuevo **no** lleva `[Install]`;
  se agrega a `GRUPOS` en `panel/panel.py` (orden = orden de arranque; se apaga al revés).
- Si usa el disco de datos, `"disco": True`: el Panel no lo enciende sin el disco montado.

## §3 Dónde vive cada cosa
- **Archivos** → disco de datos (`~/nas/datos`). **Configuración y bases de datos** → `appdata/`, en el disco
  del sistema. La BD de Immich **jamás** en NTFS/exFAT/FAT.
- Direcciones y secretos → **solo** `.env` (y `tablero.env` para el Tablero, que no recibe el `.env` completo).
- Rutas en quadlets con `%h/nas`; el repo se clona en `~/nas`.

## §4 Privacidad (el repo es una PLANTILLA pública)
- Ningún valor de una instalación real en git: IPs, nombres de red/equipos, usuarios, claves, nombres de disco.
  Va una `${VARIABLE}` (plantillas), una lectura de `.env` (código) o un valor de ejemplo
  (`192.168.1.50`, `100.64.0.1`, `mi-nas.tu-red.ts.net`, `cambia-esto`).
- Lo hace cumplir `scripts/verificar-sin-datos-personales.sh` (pre-commit; instálalo con `--instalar`) con
  dos capas: reglas generales + `privado/patrones-personales.txt`, que solo existe en tu máquina.

## §5 Desde el contenedor del Tablero
- `siteMonitor` usa `host.containers.internal`, **nunca** la IP del NAS (desde el contenedor no llega).
- `HOMEPAGE_ALLOWED_HOSTS` en `tablero.env` debe listar cada dirección desde la que se abre.

## §6 Verificar antes de cerrar un cambio
- `python3 -m unittest discover -s tests -v` verde.
- `bash -n` en los `.sh`; `scripts/verificar-sin-datos-personales.sh` verde.
- Un cambio al Panel o a un quadlet se prueba en una instalación real antes de llamarlo listo.

## §7 Git
- Ramita desde `develop` → PR con squash a `develop`. Nunca push a `develop`/`main`; `main` es solo para releases.
