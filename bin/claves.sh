#!/usr/bin/env bash
# Muestra los usuarios y claves del NAS, leídos de ~/nas/.env (la única fuente de verdad).
# No guarda copia: si cambias una clave en .env, aquí sale la nueva.  Uso: ~/nas/bin/claves.sh
set -euo pipefail
ENV="$(cd "$(dirname "$0")/.." && pwd)/.env"
v() { grep -m1 "^$1=" "$ENV" | cut -d= -f2-; }
IP="$(v NAS_IP)"
fila() { printf '%-22s %-30s %-12s %s\n' "$1" "$2" "$3" "$4"; }
fila "SERVICIO" "DIRECCIÓN" "USUARIO" "CLAVE"
fila "Panel de encendido" "http://$IP:3001" "$(v PANEL_USUARIO)" "$(v PANEL_PASSWORD)"
fila "Samba (carpetas red)" "\\\\$IP" "$(v SMB_USUARIO)" "$(v SMB_PASSWORD)"
fila "FileBrowser (admin)" "http://$IP:8081" "admin" "$(v FILEBROWSER_ADMIN_PASSWORD)"
fila "Syncthing" "http://$IP:8384" "$(v ST_USUARIO)" "$(v ST_PASSWORD)"
fila "Immich (base datos)" "interna, no se usa a mano" "$(v DB_USERNAME)" "$(v DB_PASSWORD)"
