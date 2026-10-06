# Cómo editar el Tablero

El Tablero (`http://<NAS_IP>:3000`) se arma con archivos de texto en:

```
~/nas/appdata/homepage/
├─ services.yaml   ← LOS MOSAICOS (esto es lo que más vas a cambiar)
├─ settings.yaml   ← título, colores, orden y columnas de los grupos
├─ widgets.yaml    ← la barra de arriba (CPU, memoria, disco, fecha)
├─ custom.css      ← el estilo (fondo, bordes, tamaños)
├─ bookmarks.yaml  ← enlaces rápidos sin estado (hoy vacío a propósito)
├─ docker.yaml     ← opcional: lector de Docker (ver abajo)
└─ respaldos/      ← copias de cómo estaba antes de cada cambio grande (créala tú)
```

Ábrelos con cualquier editor de texto (por ejemplo `gnome-text-editor ~/nas/appdata/homepage/services.yaml`).
**Los cambios a `services.yaml` se ven con solo recargar la página.** Si cambias `settings.yaml`,
`widgets.yaml` o `custom.css` y no se ve, reinicia el Tablero:

```
systemctl --user restart nas-tablero
```

## Antes de tocar: haz una copia

```
mkdir -p ~/nas/appdata/homepage/respaldos
cp ~/nas/appdata/homepage/services.yaml ~/nas/appdata/homepage/respaldos/services.yaml.$(date +%F)
```

Si algo sale mal, regresa la copia con `cp` al revés y recarga.

## Agregar un mosaico

Copia uno que ya exista dentro del grupo que quieras y cámbiale los datos:

```yaml
- Fotos y archivos:            # ← el grupo (ya existe)
    - "Ver mis fotos y videos": # ← el nombre: escribe lo que HACE al tocarlo
        icon: immich.png
        href: http://<NAS_IP>:2283
        description: "Qué pasa al tocarlo + qué necesitas antes."
        siteMonitor: http://host.containers.internal:2283/api/server/ping
        statusStyle: dot
```

Qué es cada línea:

| Línea | Para qué | ¿Obligatoria? |
|---|---|---|
| nombre (entre comillas) | Lo que se lee grande. Escríbelo como acción: "Ver…", "Abrir…", "Encender…" | sí |
| `icon` | El dibujo. Nombre de una app (`immich.png`, `portainer.png`…) o uno genérico `mdi-<nombre>` | no |
| `href` | A dónde lleva al tocarlo. **Sin `href` el mosaico es solo informativo** (no hace nada al tocarlo) | no |
| `description` | La letra chica. Explica qué pasa y qué hay que prender antes | no |
| `siteMonitor` | La dirección que se revisa para el punto verde/rojo | no |
| `statusStyle: dot` | Muestra el punto de color en vez de un número | va junto con `siteMonitor` |

### Las 4 reglas que rompen el Tablero si se olvidan

1. **La sangría es con ESPACIOS, nunca tabulador**, y tiene que quedar alineada igual que los de arriba
   (grupo: 0 espacios · mosaico: 4 · sus datos: 8). Una sangría chueca = el Tablero sale en blanco o con error.
2. **Si el texto lleva `:` o empieza con un símbolo, ponlo entre comillas** `"así: con comillas"`.
3. **En `siteMonitor` usa `host.containers.internal`, NUNCA la IP del NAS.** El Tablero vive en un
   contenedor y desde ahí la IP del NAS no llega a la PC: el punto saldría siempre rojo.
   En `href` sí va la IP del NAS (ese lo abre tu navegador, no el contenedor).
4. **El nombre de un grupo en `settings.yaml` debe ser IDÉNTICO al de `services.yaml`** (acentos incluidos);
   si no, el grupo pierde su ícono y su número de columnas.

## Mostrar si un contenedor de Docker está corriendo

Si además usas Docker, el Tablero puede leer el estado de sus contenedores a través de un **lector de solo lectura**
(nunca le des el socket de Docker directo). Una vez:

```bash
docker run -d --name lector-docker --restart always -p 172.17.0.1:2375:2375 \
  -v /var/run/docker.sock:/var/run/docker.sock:ro -e CONTAINERS=1 -e POST=0 tecnativa/docker-socket-proxy
```

Descomenta `docker-pc` en `docker.yaml` (solo lista contenedores; detener, exec e imágenes dan 403 y desde la
LAN no se ve). Luego agrega al mosaico estas 2 líneas (el nombre sale de `docker ps`):

```yaml
        server: docker-pc
        container: nombre-del-contenedor
```

Solo **lee**: arrancar o detener se hace en Portainer.

**Resumen de Portainer** (en ejecución / detenidos / total): crea una llave en Portainer (My account → Access
tokens), ponla en `HOMEPAGE_VAR_PORTAINER_KEY` de `~/nas/tablero.env`, descomenta el mosaico de Portainer en
`services.yaml` y `systemctl --user restart nas-tablero` (el Tablero solo lee la llave al arrancar; sin reiniciar
sale "Invalid JWT token").

## Cambiar algo que ya existe

- **Cambiar el texto:** edita el nombre o la `description` en `services.yaml` y recarga.
- **Mover un mosaico a otro grupo:** corta sus líneas y pégalas debajo del otro grupo (respeta la sangría).
- **Cambiar el orden de los grupos:** en `settings.yaml`, bajo `layout:`, el orden de arriba a abajo es el orden en pantalla.
- **Más o menos columnas en un grupo:** `columns:` en `settings.yaml`.
- **Que un grupo salga cerrado:** `initiallyCollapsed: true` en `settings.yaml` (así está "Desde fuera de casa").
- **Quitar un mosaico:** borra sus líneas (desde el `- "Nombre":` hasta antes del siguiente).

## Íconos

- Apps conocidas: `<app>.png`. Lista completa en https://dashboardicons.com (busca la app y usa el nombre que sale).
- Genéricos: `mdi-<nombre>` de https://pictogrammers.com/library/mdi/ (p. ej. `mdi-power`, `mdi-folder-network`).
- Si el ícono sale roto (un cuadrito con "logo"), el nombre no existe: prueba otro.

## Si algo sale mal

- **Página en blanco o con error:** casi siempre es sangría o comillas. Ve el error con
  `podman logs --since 5m nas_tablero` o regresa la copia de `respaldos/`.
- **Un punto rojo que debería estar verde:** revisa que `siteMonitor` use `host.containers.internal`
  y que el servicio esté prendido en el Panel (Fotos, Archivos, Syncthing, Samba y el Windows arrancan a demanda).
- **Error 400 al abrir el Tablero desde otra dirección:** esa dirección tiene que estar en `HOMEPAGE_ALLOWED_HOSTS`
  de `~/nas/tablero.env`; luego `systemctl --user restart nas-tablero`.

- **Recién reiniciado sale en inglés o con grupos de ejemplo ("My First Group"):** es normal por unos
  segundos; el Tablero se regenera solo al abrirlo en el navegador. Si no, recarga la página.

## Qué NO se configura aquí

- **Encender/apagar servicios:** eso es el Panel (`panel/panel.py`), no el Tablero.
- **El punto del Windows** lo calcula el Panel en `http://…:3001/salud/vm`: verde solo si la VM está prendida
  **y** su RDP ya contesta.

Documentación oficial completa: https://gethomepage.dev/configs/services/
