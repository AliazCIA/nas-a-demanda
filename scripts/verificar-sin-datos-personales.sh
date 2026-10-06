#!/usr/bin/env bash
# verificar-sin-datos-personales.sh — frena que datos de TU instalación (IPs, nombres, claves) lleguen a git.
# El repo es una PLANTILLA pública: solo lleva cómo se arma; tus valores viven en .env y appdata/.
#
# Dos capas:
#  1) Reglas GENERALES (valen para cualquier colaborador): nada de privado/, secretos (.env, samba.env,
#     user-mapping.xml), appdata/, bases de datos, llaves/certificados ni respaldos.
#  2) Patrones PERSONALES (tu IP, tu red Tailscale, tu usuario, el nombre de tu disco…): una expresión
#     regular por renglón en privado/patrones-personales.txt. Ese archivo vive SOLO en tu máquina,
#     porque la lista misma es dato personal. Sin el archivo, esta capa se omite.
#
# Uso:  scripts/verificar-sin-datos-personales.sh            → revisa lo rastreado en el árbol
#       scripts/verificar-sin-datos-personales.sh --staged   → revisa lo que va en el commit
#       scripts/verificar-sin-datos-personales.sh --instalar → lo instala como pre-commit local
# Sale con 1 si encuentra algo. Ver AGENTS.md §Privacidad.
set -uo pipefail

raiz="$(git rev-parse --show-toplevel)"
cd "$raiz"

if [[ "${1:-}" == "--instalar" ]]; then
    gancho="$(git rev-parse --git-path hooks)/pre-commit"
    printf '#!/usr/bin/env bash\nexec "%s" --staged\n' "$raiz/scripts/verificar-sin-datos-personales.sh" > "$gancho"
    chmod +x "$gancho"
    echo "✔ Instalado como pre-commit en $gancho"
    exit 0
fi

modo=(); [[ "${1:-}" == "--staged" ]] && modo=(--cached)
fallas=0

# Capa 1 — archivos que nunca deben estar en git.
prohibidos="$(git ls-files "${modo[@]}" | grep -E '^(privado/|\.claude/memory/privado/|appdata/|datos(/|$))|(^|/)(\.env|tablero\.env|samba\.env|user-mapping\.xml)$|\.(db|db-wal|db-shm|sqlite|pem|key|crt|bak[^/]*|pdf|xlsx?)$' || true)"
if [[ -n "$prohibidos" ]]; then
    echo "✖ Archivos que no pueden ir a git (privado/, secretos, appdata/, bases de datos, llaves):" >&2
    echo "$prohibidos" | sed 's/^/    /' >&2
    fallas=1
fi

# Capa 2 — patrones personales del dueño de los datos (local).
patrones="$raiz/privado/patrones-personales.txt"
if [[ -f "$patrones" ]]; then
    lista="$(grep -vE '^\s*(#|$)' "$patrones")"
    if [[ -n "$lista" ]]; then
        # grep archivo por archivo y no `git grep -f`: con muchos patrones a la vez, git grep dio
        # coincidencias falsas en renglones con caracteres como «…» o «→» (2026-10-05).
        hallazgos=""
        while IFS= read -r archivo; do
            [[ "$archivo" == scripts/verificar-sin-datos-personales.sh ]] && continue
            if [[ ${#modo[@]} -gt 0 ]]; then
                encontrado="$(git show ":$archivo" 2>/dev/null | grep -nIE -f <(echo "$lista") 2>/dev/null)" || continue
            else
                [[ -f "$archivo" ]] || continue
                encontrado="$(grep -nIE -f <(echo "$lista") "$archivo" 2>/dev/null)" || continue
            fi
            hallazgos+="$(printf '%s\n' "$encontrado" | sed "s#^#$archivo:#")"$'\n'
        done < <(git ls-files "${modo[@]}")
        if [[ -n "$hallazgos" ]]; then
            echo "✖ Datos personales en archivos rastreados por git:" >&2
            echo "$hallazgos" | cut -c1-160 | sed 's/^/    /' >&2
            fallas=1
        fi
    fi
else
    echo "ℹ Sin privado/patrones-personales.txt: solo se revisaron las reglas generales." >&2
fi

if [[ $fallas -eq 0 ]]; then
    echo "✔ Sin datos personales en lo que va a git."
else
    echo "  Cámbialos por una variable de .env o un valor de ejemplo (AGENTS.md §Privacidad)." >&2
fi
exit $fallas
