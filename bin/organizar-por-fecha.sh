#!/bin/bash
# Vista LEGIBLE de la biblioteca de Immich, por PERSONA y por FECHA:
#   fotos-por-fecha/<persona>/<AÑO>/<AÑO-MM-DD>/{fotos,videos}/<nombre-original>
# Usa ENLACES DUROS: no duplica espacio (mismo inodo, dos nombres).
# Idempotente: se puede correr las veces que sea.
set -euo pipefail
BASE="${1:-$HOME/nas/datos}"
DEST="$BASE/fotos-por-fecha"
SRC_REAL="$BASE/fotos"
# Immich y el disco se encienden a demanda: si falta alguno, no hay nada que organizar.
[ -d "$SRC_REAL" ] || { echo "disco no conectado, nada que hacer"; exit 0; }
podman container exists immich_postgres && [ "$(podman inspect -f '{{.State.Running}}' immich_postgres)" = true ] \
  || { echo "Immich apagado, nada que hacer"; exit 0; }
mkdir -p "$DEST"

nuevos=0; ya=0; fallos=0
while IFS='|' read -r persona tipo dia nombre ruta; do
  [ -z "${ruta:-}" ] && continue
  real="${ruta/\/data/$SRC_REAL}"
  [ -f "$real" ] || { fallos=$((fallos+1)); continue; }
  anio="${dia%%-*}"
  case "$tipo" in VIDEO) sub="videos";; *) sub="fotos";; esac
  dir="$DEST/$persona/$anio/$dia/$sub"
  mkdir -p "$dir"
  destino="$dir/$nombre"
  if [ -e "$destino" ]; then
    if [ "$(stat -c %i "$destino" 2>/dev/null)" = "$(stat -c %i "$real" 2>/dev/null)" ]; then
      ya=$((ya+1)); continue
    fi
    destino="$dir/${nombre%.*}_$(basename "${real%.*}" | cut -c1-6).${nombre##*.}"
    [ -e "$destino" ] && { ya=$((ya+1)); continue; }
  fi
  if ln "$real" "$destino" 2>/dev/null; then nuevos=$((nuevos+1)); else fallos=$((fallos+1)); fi
done < <(podman exec immich_postgres psql -U postgres -d immich -t -A -F'|' -c \
  "SELECT lower(regexp_replace(split_part(u.name,' ',1),'[^a-zA-Z0-9]','','g')),
          a.type, to_char(a.\"fileCreatedAt\",'YYYY-MM-DD'), a.\"originalFileName\", a.\"originalPath\"
   FROM asset a JOIN \"user\" u ON u.id = a.\"ownerId\"
   WHERE a.\"deletedAt\" IS NULL ORDER BY a.\"fileCreatedAt\";" 2>/dev/null)

echo "enlazados nuevos: $nuevos | ya estaban: $ya | no encontrados: $fallos"
