# Cambios y errores corregidos — 0.7.1-sd685.3 (v3) → 0.7.1-sd685.4 (v4)

Base: v3 (`../v3`, parches `0001–0016`). La v4 añade `patches/0017–0021`. Todo lo de la v3 se conserva
(tiempos de inicio, `-noverifyfiles`, caché del runtime, Xbox Cloud, estadísticas, perfiles, descargas).
Paquete, firma y `versionCode` sin cambios: se actualiza encima sin perder datos. Copia de seguridad del
estado v3 antes de empezar: etiqueta git `sd685-v3-backup` (commit `6462186`) y la APK v3 intacta en
`../v3/apk/`.

## Errores encontrados (en tus registros) y corregidos

| # | Problema | Causa (evidencia en `ANALISIS.md`) | Corrección |
|---|---|---|---|
| 1 | "Esperando el primer fotograma de Steam" para siempre | El compositor de Steam (`CCompositorGLThread`) no obtiene OpenGL a través de los *thunks* de FEX; Steam reinicia su ayudante web cada ~45 s (23 veces) | Antes de arrancar el cliente se **prueba de verdad** qué OpenGL funciona en tu teléfono (GPU y, si falla, software) y solo se usa uno que haya creado un contexto |
| 2 | El watchdog de la v3 no hacía nada | **Error mío**: moría en silencio por `set -e` en su primer `grep` sin resultados; mis pruebas usaban `bash -u` y no lo vieron | `set +e` dentro del watchdog; **todas** las pruebas se ejecutan ahora con `set -eu`, como en el teléfono, incluida una de regresión |
| 3 | No se detectaban los reinicios de `steamwebhelper` | El watchdog solo miraba fallos del proceso GPU de Chromium y un cliente parado | Cuenta los fallos de OpenGL del compositor (`webhelper.txt`) y los reinicios del ayudante (`steamui_html.txt`) desde el arranque actual, aunque Steam rote sus registros |
| 4 | Posible bucle infinito de reinicios | Steam reinicia el ayudante indefinidamente | Con 4 reinicios (`BL_X64_WATCH_RESTARTS`) se detiene Steam y la pantalla de carga lo explica; el paso a OpenGL por software ocurre **una sola vez por sesión** |
| 5 | El "modo software" de la v3 no podía arreglarlo | Solo quitaba la GPU a Chromium (`-cef-disable-gpu`); el compositor de Steam seguía sin OpenGL | El modo software da al **proceso del cliente** el OpenGL por software del rootfs x86 (llvmpipe), y solo si se ha comprobado que funciona |
| 6 | Re-descarga inútil del cliente (~700 MB) | Tras 2 arranques sin imagen se "reparaba" el cliente aunque la causa fuera OpenGL (tu registro, 22:57:03) | Si el watchdog vio una causa de OpenGL, no se descarga de nuevo; una reparación pedida por ti sí se hace y además vuelve a comprobar OpenGL |
| 7 | El Proton ARMv8.0 no se instalaba nunca | Se usaba como base el DroidDeck-Proton 11-12.8 instalado, cuyo `d3d12.dll` cambian las actualizaciones automáticas de componentes; copiaba 2 GB y fallaba en cada inicio | Se comprueban antes de copiar los archivos que cambian los componentes; si la base no es la original, se descarga (una vez, reanudable) la versión publicada y verificada. Tu herramienta instalada no se toca |
| 8 | Los componentes podían estropear el Proton ARMv8.0 ya instalado | El gestor de componentes trataba igual esa herramienta: un DXVK/vkd3d/FEX nuevo traería de vuelta las instrucciones LSE | El gestor de componentes ya no la lista (ni para cambios manuales ni automáticos) |
| 9 | Registros de Steam ilegibles en el ZIP | Sus nombres se cifraban (`entry-…`) | Nombres fijos de Steam y de DroidDeck se conservan (no son datos personales); se añade la decisión de OpenGL |

## Cómo decide la v4 el OpenGL (`droiddeck-steam-x64`)

1. **Antes de arrancar el cliente** (`x64_gl_mode`), una vez y de nuevo solo si cambia FEX, el rootfs o el
   controlador: ejecuta el `glxinfo -B` x86 del rootfs a través de FEX en la pantalla de la sesión,
   - primero por la GPU (*thunks* de FEX, como hasta ahora);
   - si no crea un contexto, con OpenGL por software (llvmpipe del rootfs, `LIBGL_ALWAYS_SOFTWARE=1`).
   Un modo cuenta solo si `glxinfo` imprimió un *renderer* (glxinfo sale con 0 también cuando falla: lo
   comprobé con el rootfs real). Resultado en `~/.droiddeck-x64/.droiddeck-gl-mode` y en
   `x64-gl-probe.txt` del ZIP. Si no se puede comprobar (sin `glxinfo` o sin pantalla), no se decide ni se
   guarda nada.
2. **Mientras arranca** (`x64_first_frame_watch`, hasta el primer fotograma):
   - en GPU: con 1 fallo de OpenGL del compositor o 2 reinicios del ayudante → comprueba el software; si
     funciona, reinicia Steam **una vez** con OpenGL por software; si no, lo dice y sigue;
   - con 4 reinicios del ayudante (cualquier modo) → detiene Steam y lo explica, en vez de repetir sin fin;
   - un cliente sin actividad 3 min: como en la v3, pero solo pasa a software si está verificado;
   - cada 30 s: "Steam sigue arrancando · tiempo · CPU · memoria · reinicios del ayudante".

La GPU **no se desactiva indiscriminadamente**: si la prueba por GPU crea un contexto, se usa la GPU; el
software solo entra si la GPU falla de verdad en tu teléfono, y los juegos siguen usando la GPU.

## Parches

- `0017 fix(steam)`: OpenGL verificado para las ventanas del cliente x86-64, watchdog nuevo (reinicios del
  ayudante, fallos del compositor, límite sin bucles), sin re-descarga inútil; textos de la pantalla de carga
  (en, es, es-419); pruebas con tus líneas de registro reales; documentación técnica.
- `0018 fix(proton)`: instalador ARMv8.0 con base modificada; el gestor de componentes excluye la versión ARMv8.0.
- `0019 chore(diagnostics)`: nombres legibles en el ZIP y la decisión de OpenGL.
- `0020 fix(proton)`: el mensaje de la descarga única del Proton ARMv8.0, traducido en la pantalla de carga.
- `0021 chore(steam)`: cada error distinto de OpenGL una sola vez en el registro (Mesa repite sus errores).

Archivos: `tools/linuxfs/overlay/usr/local/bin/droiddeck-steam-x64`, `droiddeck-proton-armv80`,
`session/LoadingState.kt`, `session/ComponentsManager.kt`, `session/EnhancedSessionLogShare.kt`,
`session/DiagnosticsExtras.kt`, `res/values*/strings.xml`, `docs/development/x86-64-steam-client.md`.
Pruebas nuevas/reescritas: `tools/tests/test_steam_first_frame_watch.py` (36),
`tools/tests/test_armv80_install_base.py` (5), `LoadingStepExplainedTest.kt` (+2),
`Armv80ProtonComponentsTest.kt` (1).
