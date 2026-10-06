# Bitácora — nas-a-demanda

> Append-only con `>>`, una línea por entrada (`merge=union`). Qué se hizo, qué falló, cómo se corrigió.

- 2026-10-06 · Repo creado como plantilla pública a partir de una instalación real: Panel parametrizado por `.env` (VM opcional, nombre de disco), Guacamole pasado de `podman generate systemd` a quadlets (`nas-guacd`/`nas-guacamole`), Tablero como plantillas con `${VARIABLES}` que `instalar.sh` llena una vez, `HOMEPAGE_ALLOWED_HOSTS` movido a `tablero.env`, 10 pruebas del Panel, pre-commit de datos personales adaptado de AdminGastos.
