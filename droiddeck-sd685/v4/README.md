# DroidDeck 0.7.1-sd685.4 (v4) — Redmi Note 13 (Snapdragon 685 / Adreno 610)

Continúa la v3 (`../v3`), la v2 (`../v2`) y la v1 (`../`), que se conservan intactas como copia de seguridad.
Todas sus funciones siguen. Esta versión se basa en **tus registros reales**
(`DroidDeck-2026-11-21-01-steam.zip`, 0.7.1-sd685.3): primero el análisis, luego el código.

## Qué estaba pasando (con evidencia, ver `ANALISIS.md`)

- El cliente Steam x86-64 arranca bien bajo FEX, pero **el compositor propio de Steam no consigue un contexto
  OpenGL** (`failed to acquire a gl context`, 14 veces): en tu teléfono no hay nodo DRM para las apps, así que
  el OpenGL por GPU de los programas x86 falla (`failed to create dri3 screen`, `failed to load driver: zink`).
- Entonces **Steam reinicia su ayudante web cada ~45 s, para siempre** (23 veces) y nunca crea su ventana:
  el compositor de DroidDeck recibe 0 imágenes. No es que el primer fotograma no se detecte: no existe.
- El proceso GPU de Chromium **no** falla (0 caídas; funciona sin GL). Las opciones de GPU de CEF no eran la causa.
- El watchdog de la v3 **murió en silencio** al empezar (error mío con `set -e`) y, además, vigilaba otras
  señales y su "modo software" no daba OpenGL al compositor. También volvió a descargar el cliente sin motivo.
- El Proton ARMv8.0 fallaba porque las actualizaciones automáticas de componentes habían cambiado el
  `d3d12.dll` del DroidDeck-Proton instalado que usaba como base.

## Qué hace la v4 (ver `CAMBIOS.md`)

1. **Comprueba en tu teléfono** qué OpenGL funciona para el cliente x86-64 (GPU primero; si falla, OpenGL por
   software llvmpipe) con el `glxinfo` x86 a través de FEX, y **solo usa uno que haya creado un contexto**. No
   desactiva la GPU si la GPU funciona; los juegos siguen con la GPU. Comprobado en una CPU ARMv8.0 emulada
   con tu FEX, el runtime de DroidDeck y tu rootfs: la GPU falla como en tu teléfono y el software crea un
   contexto OpenGL 4.6, así que la v4 elige software.
2. **Watchdog nuevo**: detecta los fallos de OpenGL del compositor y los **reinicios de `steamwebhelper`** (no
   solo la muerte del cliente), pasa a OpenGL por software verificado **una sola vez**, y con 4 reinicios
   **detiene Steam en vez de repetir sin fin**, explicándolo en pantalla.
3. No vuelve a descargar el cliente cuando la causa es OpenGL.
4. **Proton ARMv8.0** corregido por separado: detecta la base modificada antes de copiar 2 GB y usa la versión
   original verificada; el gestor de componentes ya no toca la versión ARMv8.0.
5. ZIP de registros más legible (nombres reales de los registros de Steam) y con la decisión de OpenGL.

## Contenido

| Archivo | Qué es |
|---|---|
| [`ANALISIS.md`](ANALISIS.md) | Análisis de tu ZIP, respuesta a cada pregunta, qué está confirmado y qué no |
| [`CAMBIOS.md`](CAMBIOS.md) | Cambios, errores encontrados y corregidos, parches |
| [`PRUEBAS.md`](PRUEBAS.md) | **Probado en el contenedor** vs **pendiente en tu teléfono**, por separado |
| [`INSTALACION.md`](INSTALACION.md) | Actualizar sin perder datos, qué verás, qué registros enviarme |
| [`LIMITACIONES.md`](LIMITACIONES.md) | Lo no demostrado, qué hacer si no funciona, recomendaciones |
| `apk/` | `DroidDeck-0.7.1-sd685.4.apk` y `SHA256SUMS` |
| `fuentes/` | Código fuente completo de la v4 |
| `patches/` | `0017–0021` (encima de `../v3/patches/0013–0016`, `../v2/patches/0009–0012`, `../patches/0001–0008`) |
| `evidencia/` | Cifras de tus registros, pruebas con el rootfs x86 y el cliente Steam reales, salidas de los tests |

## Importante

- **No la he probado en tu Redmi Note 13.** Todo lo de `PRUEBAS.md` marcado como contenedor se ejecutó aquí;
  nada de eso demuestra que el menú de Steam aparezca en tu teléfono. **Necesito tus registros de la v4**
  (ver `INSTALACION.md`).
- Con OpenGL por software el **menú de Steam será lento**. Es la alternativa que funciona sin acceso DRM a la
  GPU; la vía rápida (OpenGL por GPU para programas x86 en tu teléfono) queda como mejora futura
  (`LIMITACIONES.md`).
- Actualiza encima de la v1/v2/v3 **sin borrar datos** (mismo paquete y firma). No borra juegos, runtime,
  cuentas ni configuraciones. No requiere root.
