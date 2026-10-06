# Decisiones

Qué se decidió y por qué. Cada una nació de un problema real al armar el NAS (septiembre de 2026).

## Arquitectura

- **Todo a demanda, salvo Tablero y Panel.** El disco de datos externo lo monta la sesión gráfica, *después*
  de que arrancan los servicios de usuario: un servicio que arranca solo encontraría la carpeta vacía y
  escribiría en el disco del sistema o fallaría en silencio. Además la PC es de uso diario y no debe
  gastar RAM en lo que no se usa (Immich solo, ~2.5 GB).
- **El Panel verifica el disco por dispositivo, no por ruta.** "Montado" = `~/nas/datos` resuelve a un
  directorio de *otro* sistema de archivos que `$HOME`. Una carpeta vacía en el mismo disco no cuenta.
- **podman rootless + quadlets** en vez de Docker Compose: cada servicio es una unidad de systemd del usuario
  (`systemctl --user start immich-server`), así el Panel enciende y apaga sin root y sin socket de Docker.
- **Panel en Python sin dependencias:** nada que instalar ni actualizar; un archivo y una página.
- **`appdata/` en el disco del sistema:** la documentación de Immich prohíbe su base de datos en NTFS
  ("It will not work on any filesystem formatted in NTFS or ex/FAT/32").
- **Un solo `.env`** como fuente de verdad. El Tablero recibe aparte `tablero.env` (solo su llave y sus
  direcciones) para no exponer todas las claves dentro de su contenedor.
- **FileBrowser Quantum** (`gtsteffaniak/filebrowser`) en vez del File Browser original, que está archivado.

## Tablero (Homepage)

- **`siteMonitor` con `host.containers.internal`:** desde el contenedor, la IP de la PC en la LAN no responde
  (el monitor salía siempre rojo).
- **`bookmarks.yaml` con `[]`**: con `- {}` Homepage muestra enlaces de ejemplo.
- **"¿El Windows está listo?" es solo un indicador.** RDP no es HTTP, así que el Panel expone
  `/salud/vm`: 200 si la VM está encendida **y** su puerto 3389 ya acepta conexiones (Windows tarda en
  arrancar). Un botón que abriera RDP no sirve: `rdp://` en Chrome de Android queda bloqueado.

## VM de Windows

- La VM vive en la NAT de libvirt (no se ve desde la LAN). `sistema/rdp-vm.service` la publica con `socat`
  en el 3389 de la PC — es de sistema porque un puerto < 1024 exige privilegio.
- **Guacamole** como respaldo: la VM dentro del navegador, sin instalar app.

## Acceso desde fuera

- **Solo Tailscale; nunca abrir puertos en el módem.** El Panel desde fuera va por `tailscale serve`
  (HTTPS con certificado real, solo dentro de la red Tailscale).
- **Tailnet Lock** activo: solo entran equipos firmados por uno de confianza; por eso no hace falta otra
  contraseña delante del Tablero.
- En la PC Tailscale queda **siempre** prendido: apagarlo desde el Panel estando fuera te dejaría sin forma de volver.

## Pendientes conocidos

- Un solo disco **no es respaldo**: falta una segunda copia.
- La biblioteca de fotos de Immich en NTFS funciona, pero la documentación recomienda un sistema de archivos Unix.
- En la LAN el Panel va por HTTP en claro (Basic auth); desde fuera ya va por HTTPS.
