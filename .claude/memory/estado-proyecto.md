---
name: estado-proyecto
description: Backlog durable de nas-a-demanda — lee la sección 🧭 BACKLOG al tope.
metadata:
  type: project
---

# Estado del proyecto — nas-a-demanda

> **Aquí empiezas.** Backlog DURABLE del proyecto. Cerrado → `bitacora.md`. Cómo mantenerlo → skill `to-do` / `cerrar-slice`.

## 📌 Dónde estamos (resumen vivo)
Plantilla extraída de una instalación real que funciona (Panel, Tablero, Immich, Syncthing, FileBrowser,
Samba, VM + Guacamole, Tailscale). Panel cubierto por pruebas; `instalar.sh` probado solo en su llenado de
plantillas — falta correrlo de punta a punta en una máquina limpia.

## 🧭 BACKLOG
> **KEY:** `📘` tiene plan · `➖` mecánico · `📝` necesita plan.

### 📬 PRs/MRs abiertos esperando OK
(ninguno abierto)

### 📘+➖ 1 — Abierto a la espera del GO, o de decisión puntual
- 📘 [pending] Probar `instalar.sh` de punta a punta en una máquina/VM limpia (Fedora) y corregir lo que salga.
- 📘 [pending] Que la instalación viva del dueño corra DESDE un clon de este repo (hoy es una copia aparte) — así lo vivo y lo publicado no se separan.
- ➖ [pending] CI en GitHub Actions: pruebas del Panel + capa 1 del verificador de datos personales + `bash -n`.

- ➖ [pending] Fijar versiones de imágenes (hoy `:latest`/`:release`) + `AutoUpdate=registry` para actualizar a propósito, no por sorpresa. (Revisión 2026-10-06, severidad MEDIA.)
- ➖ [pending] `HealthCmd` en los quadlets para que el Panel distinga "arrancando" de "listo". (Revisión 2026-10-06, BAJA.)
- ➖ [pending] Capturas del Panel y el Tablero en el README. (Revisión 2026-10-06, BAJA.)

### 📝 2 — Abierto pero necesita plan
- Segunda copia de los datos (un solo disco no es respaldo) + respaldo de `appdata/` con `pg_dump` de Immich (restic/borg). (Revisión 2026-10-06, severidad ALTA: es el riesgo real de perder fotos.)
- Servicios del Panel declarados en un YAML (no en `GRUPOS` del código) para que quien clone agregue/quite servicios sin tocar Python. (Revisión 2026-10-06, MEDIA.)
- Login del Panel: sesión con cookie + límite de intentos en vez de Basic auth pelón. (Revisión 2026-10-06, MEDIA.)
- HTTPS del Panel en la LAN (hoy solo desde fuera, por `tailscale serve`).

## 🪦 Deprecated / Fuera por decisión (NO reabrir)
- Reescribir el Panel en Blazor/.NET (evaluado 2026-10-06, recomendación de Claude, pendiente de que el dueño lo confirme): para ~200 líneas y 6 botones agrega SDK, compilación y RAM, y rompe "clonar y correr". Se reabre solo si el Panel crece a app real (usuarios, historial, BD).
- Botón que abra RDP desde el Tablero: `rdp://` queda bloqueado en Chrome Android → solo indicador `/salud/vm`.
- Abrir puertos en el módem: todo lo de fuera va por Tailscale.

## 🧠 Decisiones de arquitectura (con su porqué)
Viven en `DECISIONES.md` (raíz) — no se duplican aquí.
