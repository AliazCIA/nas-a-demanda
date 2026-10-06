# Acceso desde fuera de casa (Tailscale)

**Regla: nunca abras puertos en el módem.** Todo lo de fuera va por [Tailscale](https://tailscale.com),
una red privada entre tus propios aparatos.

## Montarlo

1. Instala Tailscale en la PC y entra con tu cuenta: `sudo tailscale up`. Anota su IP (`tailscale ip -4`) en
   `NAS_TAILSCALE_IP` y su nombre MagicDNS en `NAS_TAILSCALE_DNS` (`.env`), y agrega `<NAS_TAILSCALE_IP>:3000`
   a `HOMEPAGE_ALLOWED_HOSTS` (`tablero.env`).
2. Instala Tailscale en el celular con la misma cuenta.
3. **Panel con HTTPS** (certificado real, solo visible dentro de tu red Tailscale):
   ```bash
   sudo tailscale serve --bg --https=443 http://127.0.0.1:3001   # persiste al reiniciar
   sudo tailscale serve --https=443 off                          # para quitarlo
   ```
   Desde fuera abre `https://<NAS_TAILSCALE_DNS>`.
4. El Tablero e Immich desde fuera: `http://<NAS_TAILSCALE_IP>:3000` y `:2283`.

## Endurecerlo

- **Tailnet Lock** (`tailscale lock init`): solo entran equipos firmados por uno de confianza. Guarda los
  códigos de desactivación de emergencia **fuera** de la PC (papel o gestor de contraseñas).
- Equipo nuevo con Tailnet Lock: entra bloqueado; en la consola → Máquinas copia el
  `tailscale lock sign nodekey:... tlpub:...` y córrelo en la PC.
- Otra persona: consola → Usuarios → Invitar usuario (con su propia cuenta).
- En la PC Tailscale queda **siempre** prendido; el túnel se prende y apaga en el celular.

## Immich en el celular

En la app de Immich: dirección local `http://<NAS_IP>:2283` (en la WiFi de casa) y externa
`http://<NAS_TAILSCALE_IP>:2283`.
