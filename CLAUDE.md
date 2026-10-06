# 🧠 nas-a-demanda — NAS casero sobre una PC Linux: servicios a demanda con Panel + Tablero

Lo que necesitas saber para trabajar aquí:

🎯 Eres el claude que **construye y mantiene la PLANTILLA pública** de un NAS casero (podman rootless +
quadlets, Panel de encendido en Python, Tablero Homepage) que cualquiera clona en `~/nas` y replica con
su propio `.env` — sin que ningún dato de una instalación real llegue al repo.

🧠 **ANTES de construir: LEE el backlog vivo `estado-proyecto.md`, la ley del repo `AGENTS.md` y los porqués
de `DECISIONES.md`** — no re-decidas lo decidido. El detalle 1:1 de este árbol vive en `MEMORY.md`, que se
**auto-carga** con este archivo vía `@import`.

## 📁 Dónde va cada cosa

`stack/` `panel/` `systemd/` `sistema/` `plantillas/` `bin/` = el producto (ver README §Qué hay en el repo).
`.claude/` = cerebro operativo. `privado/` = patrones personales del dueño: **solo local, nunca en git**.

```
📄 CLAUDE.md
│   ├─ 🎯 Misión: plantilla replicable de NAS a demanda, sin datos de nadie
│   ├─ 🧠 Antes de construir: estado-proyecto → AGENTS.md → DECISIONES.md
│   ├─ 📁 Dónde va cada cosa: producto en la raíz · cerebro en .claude/ · lo personal en privado/
│   │
│   ├─ 🖋️ LA FIRMA (capacidades → artefactos)
│   │   ├─ Retomar el hilo ................ estado-proyecto.md + bitacora.md
│   │   ├─ Agregar/cambiar un servicio .... AGENTS.md §2 + stack/ + GRUPOS de panel/panel.py
│   │   ├─ Editar el Tablero .............. docs/tablero.md + plantillas/homepage/
│   │   ├─ Instalar / probar / operar ..... dev-operacion.md + instalar.sh + tests/
│   │   ├─ Mantener fuera los datos reales  scripts/verificar-sin-datos-personales.sh (pre-commit)
│   │   └─ Cerrar un slice ................ skill cerrar-slice (tests → memoria → PR a develop)
│   │
│   │    Meta: lo que funciona en la instalación real termina como plantilla genérica aquí.
│   │
│   └─ 🛡️ Reglas duras
▼
📄 .claude/memory/MEMORY.md
│   ├─ 📍 Dónde estamos (estado + backlog)
│   └─ 🗂️ Índice de memorias por prefijo (núcleo · dev-)
▼
📁 .claude/memory/   la memoria del proyecto (limpia: sin IPs, nombres ni claves)
```

## 🛡️ Reglas duras

- **Ley = `AGENTS.md`**: todo a demanda salvo Tablero y Panel; BD jamás en NTFS; secretos solo en `.env`.
- **Repo PÚBLICO**: ningún valor de una instalación real en git (ni en código, docs ni memoria) — `${VARIABLE}`,
  lectura de `.env` o valor de ejemplo. El pre-commit lo frena.
- **LISTO** = tests verdes citados + verificador verde + probado en una instalación real + OK del dueño.
- **Git**: ramita desde `develop` → PR con squash; nunca push a `develop`/`main`; `main` es release-only.

**⚙️ Auto-carga (`@import` de Claude Code):**

@.claude/memory/MEMORY.md
