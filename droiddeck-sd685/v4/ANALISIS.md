# Análisis de tus registros — `DroidDeck-2026-11-21-01-steam.zip` (0.7.1-sd685.3)

Analicé el ZIP completo antes de tocar el código. `device.txt` confirma la versión: **0.7.1-sd685.3**, commit
`6462186`, paquete `com.droiddeck.launcher.sd685`.

Los registros de Steam venían con nombres cifrados (`entry-…`: el ZIP cifra los nombres que no conoce). Los
identifiqué calculando el mismo hash sobre los nombres de Steam:

| En el ZIP | Archivo real |
|---|---|
| `steam/entry-880d0f6f9c9efbb6.txt` | `webhelper.txt` (el ayudante web de Steam) |
| `steam/entry-b94fac34e0729b03.txt` | `steamui_html.txt` (la interfaz del cliente) |
| `steam/entry-d20ccf3f76b94466.txt` | `console-linux.txt` (consola completa del cliente) |
| `steam/entry-f059c52eb5241d0a.txt` | `webhelper_gpu.txt` (informes del proceso GPU de Chromium) |
| `steam/entry-4d71bc0594791d02.txt` | `bootstrap_log.txt` (actualizador) |
| `entry-9d6cc98600a4c482/entry-f8d474f0acb2700e.log` | `steam-x64/steam-x64.log` (lanzador x86-64 de DroidDeck) |

(La v4 deja estos nombres legibles en el ZIP: no dicen nada personal.)

## Respuestas, con la evidencia

### 1. ¿FEX está listo y el cliente x86-64 arranca? — Sí

`steam-x64.log`: `FEX ready (fex-2611-r10, catalog)`; el cliente es la versión `1795048523`
(`steamdeck_publicbeta`) y arranca. El problema empieza después.

### 2. ¿Por qué se reinicia `steamwebhelper`? — Porque el compositor de Steam no consigue OpenGL

Lo reinicia **el propio cliente de Steam**. Secuencia real, repetida durante toda la sesión:

```
10:55:28 CCompositorGLThread::CreateOutputWindow: Creating browser window at: 0,0 size: 1280x800   (webhelper.txt)
10:55:28 Error: CreateOutputWindow: failed to acquire a gl context                                (webhelper.txt)
10:55:28 SP BPM_uid0: Failed to create output window. Falling back to system composer, previous mode: OpenGL
10:55:32 Restart webhelper process, counter 2                                                      (steamui_html.txt)
10:55:34 Startup - webhelper launched pid: 21639 …                                                 (webhelper.txt)
```

Totales: **24** intentos de crear la ventana del compositor, **14** "failed to acquire a gl context", **23**
"Restart webhelper process" (uno cada 45–50 s). Steam dibuja su menú (modo Big Picture, `BPM`) con un
compositor propio dentro de `steamwebhelper` que **necesita un contexto OpenGL**, sean cuales sean las
opciones de Chromium.

Las conexiones DevTools perdidas y recuperadas son una **consecuencia**: cada reinicio mata el ayudante y su
puerto (`session.log`: "Could not reach the client's DevTools… Errno 111", "No SharedJSContext yet").

### 3. ¿Falla el proceso GPU de CEF? ¿Problema de ANGLE/Vulkan? — CEF no falla; falla el OpenGL de los programas x86

- `console-linux.txt`: **0** "GPU process exited unexpectedly", **0** "GPU process isn't usable". El proceso GPU
  de Chromium no se cae.
- `webhelper_gpu.txt`: 27 informes, todos con `GL implementation parts: (gl=none,angle=none)` y
  `GL_RENDERER: (null)`. Chromium nunca obtuvo GL (ni ANGLE): sigue sin GPU, sin fallar. Las opciones
  `-cef-force-gpu -cef-use-gl=angle -cef-use-angle=vulkan` no consiguen ANGLE, pero eso no bloquea a Chromium.
- Lo que falla es el OpenGL que reciben los programas x86 a través de los *thunks* de FEX (Mesa del lado ARM,
  zink sobre Turnip): **100×** `glx: failed to create dri3 screen`, **100×** `failed to load driver: zink`
  (precedidos de `MESA-LOADER: failed to retrieve device information`), **8×** `failed to load driver: swrast`
  con `ZINK: vkCreateInstance failed (VK_ERROR_INCOMPATIBLE_DRIVER)`, y la consulta Vulkan del cliente
  `vkEnumeratePhysicalDevices failed`.
- En cambio el compositor de DroidDeck (lado Android) **sí** usa la GPU: `wayland.log`: "compositor renders on
  Turnip Adreno (TM) 610", Vulkan 1.3.363. La GPU funciona; lo que no funciona es el camino
  x86 → FEX → thunk → Mesa (zink) → KGSL dentro del entorno Linux.
- El propio compositor de DroidDeck explica la primera mitad: `wayland.log` 10:53:19 *"this device gives apps
  no display (DRM) device (/dev/dri)"*. Sin nodo DRM, GLX no puede crear una pantalla DRI3
  (`MESA-LOADER: failed to retrieve device information` → `failed to create dri3 screen`), y Xwayland tampoco
  tiene *glamor*. El respaldo de Mesa (zink por `drisw`) tampoco arranca: `ZINK: vkCreateInstance failed
  (VK_ERROR_INCOMPATIBLE_DRIVER)` dentro del proceso x86 traducido.
- **Sin confirmar**: por qué el Vulkan de Turnip no se puede crear desde ese camino (*thunk* de FEX → Mesa ARM →
  KGSL). No lo he podido comprobar en tu teléfono, y la v4 no depende de ello.

### 4. ¿Gamescope/Xwayland crea las ventanas? — No llega ninguna

`wayland.log`: 28 informes de 10 s, todos con `0 game frames … 0 distinct buffers` (solo el primero tiene 12
escenas: la propia pantalla de DroidDeck), y la estadística `0 windows open`. Ninguna ventana de cliente envió
nunca una imagen. No hay indicios de fallo de Xwayland ni del compositor: no reciben nada,
porque Steam no llega a crear su ventana (punto 2).

### 5. ¿Se genera el primer fotograma y DroidDeck no lo detecta? — No

No hay búferes de ningún cliente en el compositor, y Steam escribe que su ventana de salida falló. No es un
fallo de detección.

### 6. ¿Por qué el watchdog de la v3 no lo recuperó? — Dos errores míos

1. **Murió en silencio al empezar.** El lanzador usa `set -eu`; en bash, `x=$(… | grep -c …)` sin coincidencias
   devuelve 1 y `set -e` termina la función. En tu `steam-x64.log` no hay **ninguna** línea "steam is still
   starting" (el watchdog la escribe cada 30 s). Lo reproduje en el contenedor. Mis pruebas de la v3 lo
   ejecutaban con `bash -u` (sin `-e`), por eso no lo detectaron.
2. **Aunque hubiera vivido, vigilaba otras señales**: fallos del proceso GPU de Chromium (que aquí no ocurren) y
   un cliente sin actividad (aquí está ocupado reiniciando el ayudante). Y su "modo software" solo quitaba la
   GPU a Chromium (`-cef-disable-gpu`), lo que **no** da OpenGL al compositor de Steam.

Además, la reparación automática de la v3 **volvió a descargar el cliente entero** sin motivo:
`22:57:03 repairing the x86-64 Steam client (the client was started 2 times without showing anything)` y
27 paquetes descargados de nuevo. Los archivos del cliente no eran el problema.

### 7. ¿Puede funcionar un modo CEF sin aceleración GPU? — Solo no basta; hace falta OpenGL por software verificado

Chromium ya funcionaba sin GPU (`gl=none`). Lo que hace falta es OpenGL para el **compositor de Steam**. La
alternativa real es OpenGL por software (llvmpipe, del rootfs x86) para el proceso del cliente. La v4 solo la
usa **si comprueba en tu teléfono que crea un contexto** (ver `CAMBIOS.md`).

No es un invento para este caso: DroidDeck ya hace lo mismo con el cliente arm64 en GPUs Mali (Venus):
`droiddeck-session` prueba el GL de zink con `droiddeck-glprobe` y, si no arranca, *"the Steam client's GL uses
llvmpipe (software)"*. Y su gamescope está parcheado para mostrar lo que dibuja Xwayland sin *glamor* (sin nodo
DRM, como en tu teléfono): `tools/gamescope/PATCHES.md`, parche `0927` ("Xwayland has no glamor and commits a few
wl_shm buffers…"). La v4 aplica ese mismo criterio al cliente x86-64 bajo FEX, con una prueba real.

Lo que pude comprobar en el contenedor, con el **mismo rootfs x86** que descarga tu teléfono (SHA-256
`2854b06d…a178`, verificado) y el **mismo cliente** `1795048523` (detalles en `evidencia/`):

- Ese rootfs crea un contexto OpenGL 4.6 por software (`llvmpipe (LLVM 20.1.8)`, Mesa 26.1.6).
- Con un OpenGL roto al estilo de tu teléfono (zink sin Vulkan), Mesa escribe exactamente los mismos errores
  que tus registros.
- El cliente Steam real, con la configuración de software de la v4, detecta llvmpipe como GPU, arranca su
  ayudante sin ningún error de GL y dibuja sus propias ventanas.
- **No pude llegar al menú de Steam en el contenedor**: no hay internet directo para Steam y su conexión
  interna con el ayudante (websocket local) se rechazó por diferencias del entorno (error 0x3009; en tu
  teléfono esa conexión sí funciona). Por eso **no está demostrado que el menú aparezca**; eso solo lo puede
  confirmar tu teléfono.
- **Verificado en una CPU ARMv8.0** (Cortex-A53 emulado, sin LSE, las mismas *Features* que tu SD685) con
  **tu FEX 2611-r10**, el runtime Linux de DroidDeck (Ubuntu 26.04) y **tu rootfs x86**: el OpenGL por GPU a
  través de los *thunks* falla (zink, como en tu teléfono) y el OpenGL por software x86 **crea un contexto
  OpenGL 4.6** (`llvmpipe`). Las funciones reales de la v4 deciden `software` en esa máquina
  (`evidencia/vm-armv80-opengl-fex.txt`).
- Probé también una tercera vía que habría sido más rápida (el llvmpipe ARM del runtime a través de los
  *thunks*): `glxinfo` se cae con `GLXBadFBConfig`, así que **no la uso**.
- **Rendimiento**: llvmpipe bajo FEX en un Snapdragon 685 será lento (menús con pocos fps). Es un modo para
  que Steam se pueda usar, no para que vaya rápido; los juegos siguen usando la GPU.

### 8. Proton ARMv8.0: `d3d12.dll` no coincide — causa encontrada en el código

```
15:53:21 checking Proton for this CPU (ARMv8.0; …)
         droiddeck-proton-armv80: using the installed DroidDeck-Proton 11-12.8 as the base
15:53:53 installing DroidDeck-Proton 11-12.8 for ARMv8.0: rewriting 688 files
         droiddeck-proton-armv80: files/lib/wine/vkd3d-proton/aarch64-windows/d3d12.dll is not the file the patch was made for
15:53:54 Proton for ARMv8.0 could not be installed now; Windows games use droiddeck-proton-x64 until it is
```

El instalador copiaba tu DroidDeck-Proton 11-12.8 instalado (2 GB en 32 s) y luego fallaba, **en cada inicio**.
Causa: DroidDeck mantiene actualizados automáticamente los componentes (DXVK, vkd3d-proton, FEX) de los Proton
cuya carpeta empieza por "DroidDeck-Proton" (`ComponentUpdates.follows`), así que su `d3d12.dll` ya no es el de
la versión publicada para la que se hizo el parche. Corregido por separado (ver `CAMBIOS.md`).

## Conclusión

Causa del bloqueo, con evidencia: **el compositor de Steam no obtiene un contexto OpenGL a través de FEX**, así
que Steam reinicia su ayudante web cada ~45 s para siempre y nunca crea su ventana. El watchdog de la v3 no
podía arreglarlo (murió por `set -e` y vigilaba otra cosa). Lo que **no** está confirmado: el motivo exacto por
el que Mesa no accede a la GPU desde FEX en tu teléfono, y que el OpenGL por software muestre el menú allí.
