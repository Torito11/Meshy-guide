# Cambios y errores corregidos — 0.7.1-sd685.2 (v2) → 0.7.1-sd685.3 (v3)

Base: v2 (`../v2`, parches `0001–0012`), que a su vez conserva todo lo de la v1. La v3 añade
`patches/0013–0016`. Ninguna función se elimina; el paquete, la firma y el `versionCode` no cambian
(actualiza la v2 o la v1 sin borrar datos). Copia de seguridad del estado v2 antes de empezar:
etiqueta git `sd685-v2-backup` y la APK v2 sin tocar en `../v2/apk/`.

## Errores encontrados y corregidos

| # | Problema | Causa encontrada en el código | Corrección |
|---|---|---|---|
| 1 | Steam se queda en **"Esperando el primer fotograma de Steam"** sin progreso | En tu CPU el menú de Steam lo dibuja un `steamwebhelper` **x86 bajo FEX** que usa la GPU a través de los *thunks* GL de FEX (ANGLE → GL → Mesa → Turnip). Si su proceso GPU falla repetidamente, Chromium abandona ("GPU process isn't usable") y la pantalla queda vacía **para siempre**. El script ya lo detectaba (`x64_gpu_watch`) pero **solo lo anotaba en el registro**. Además, nada en pantalla explicaba qué hacía el cliente. | Vigilancia hasta el primer fotograma: reinicio **único** con renderizado por software si la GPU falla o el cliente se para 3 min (tras 5), recordado para esa versión del cliente; informe cada 30 s (tiempo, CPU del cliente, memoria libre, actualización/verificación, biblioteca que falte). **Causa probable, no confirmada en tu teléfono**: necesito tus registros para confirmarla (ver `LIMITACIONES.md`). |
| 2 | Cada arranque de Steam rehacía cientos de enlaces de bibliotecas y un `ldconfig` x86 bajo FEX | `x64_prepare` borraba y recreaba `steamrt-libs` siempre, con un proceso `basename` por archivo | Se rehace solo si cambia el runtime de Valve o el rootfs (sello); un `ln` y un `rm` por directorio. Medido en contenedor: **5,9 s → 9 ms** (0,14 s cuando hay que rehacerlo) |
| 3 | El cliente Steam re-verificaba todos sus archivos en cada arranque (lento bajo FEX) | El bootstrapper verifica siempre | Si **esa misma versión** ya llegó a la pantalla, arranca con `-noverifyfiles`; tras actualización, reparación o un arranque sin imagen verifica como siempre |
| 4 | Python se arrancaba en cada sesión solo para comprobar el Proton ARMv8.0 ya instalado | — | Comprobación en el shell (sha256 del parche vs marca) |
| 5 | El botón "Compartir registros" solo aparecía cuando la sesión **terminaba** | `EndedActions` solo con `ended` | Aparece también tras 90 s de espera, con la sesión aún en marcha |
| 6 | La descarga de 626 MB del Proton ARMv8.0 no mostraba progreso | El instalador solo escribía en el registro | Progreso real (MB en disco / total) en la pantalla de carga |
| 7 | Reproductor web de xCloud sin estadísticas fuera de su propia capa | — | Estadísticas reales de WebRTC en ambos motores, guardadas y visibles en Configuración |
| 8 | Cuenta sin regiones de Xbox Cloud: mensaje genérico "No Xbox Cloud Gaming region" | — | Explica que el servicio puede no estar disponible en tu país o suscripción y que DroidDeck no lo esquiva |
| 9 | **Regresión mía detectada por la suite de tests** durante esta versión: 9 tests de `test_steam_x64_cpu.py` fallaban | Mis comprobaciones nuevas en `x64_exec` leían `X64_HOME` con `set -u` | Se omiten si no está definido (el lanzador siempre lo define); los 9 tests vuelven a pasar sin tocarlos |

## 0013 — `fix(steam)`: vigilar el cliente x86-64 hasta su primer fotograma y recuperarlo
- `droiddeck-steam-x64`: `x64_first_frame_watch`, `x64_client_ticks`, `x64_bootstrap_active`, `x64_stop_client`;
  decisión de renderizado persistente `~/.droiddeck-x64/.droiddeck-cef-software` (por versión del cliente).
- `droiddeck-session`: borra las marcas al empezar; reinicia el cliente **una vez** para software.
- `SessionActivity.kt`: escribe `~/.bl-first-frame` cuando el compositor dibuja el primer fotograma.
- `LoadingState.kt` + textos: los nuevos pasos se muestran traducidos en la pantalla de carga.
- Tests: `tools/tests/test_steam_first_frame_watch.py` (procesos reales), `LoadingStepExplainedTest.kt`.

## 0014 — `perf(steam)`: tiempos de inicio y menos trabajo repetido
- `session/StartupTimes.kt` (nuevo): apertura de la app (arranque en frío), Linux, FEX + cliente x86-64,
  Steam (cliente → primer fotograma), total; por juego: lanzamiento → primera imagen → fluido (≥ 20 fps
  durante 3 s). Primer inicio (descargas/instalaciones) separado. Historial en `startup-times.jsonl` y
  `timings.txt` en cada carpeta de registros.
- `droiddeck-game-env`: marca cada lanzamiento de juego. `AgentGuest.kt`: usa el foco de gamescope.
- `droiddeck-steam-x64`: caché de enlaces del runtime, `-noverifyfiles` para versiones ya probadas.
- `droiddeck-steamrt-shim`: sin procesos `basename`. `droiddeck-session`: ruta rápida del Proton ARMv8.0.
- Tests: `StartupTimesTest.kt`, `test_game_launch_mark.py`, ampliado `test_steam_first_frame_watch.py`.

## 0015 — `feat(xcloud)`: región por latencia, calidad automática, estadísticas reales
- `stores/xbox/XboxCloudNetwork.kt` (nuevo): latencia TCP a cada región **oficial** de tu cuenta; otra
  región que la de Microsoft solo si gana ≥ 15 ms y ≥ 15 %.
- `stores/xbox/XboxCloudStats.kt` (nuevo): lectura de `getStats()` de WebRTC, historial, calidad de conexión,
  límite automático de bitrate.
- `stores/xbox/XboxCloudStatsPanel.kt` (nuevo): sección **Estadísticas** en la configuración de Xbox Cloud.
- `XboxNativePlayerActivity.kt`, `XboxCloudPlayerActivity.kt`: región, calidad automática y estadísticas;
  el reproductor web las obtiene con un script de inicio de documento (sin tocar `player.js`).
- `XboxCloudSettings.kt`: `autoQuality`, opción "Menor latencia medida". Perfiles Rendimiento y Xbox Cloud
  la usan.
- `session/DiagnosticsExtras.kt` (nuevo): `timings.txt`, `memory.txt`, registro del lanzador x86-64 en el ZIP.
- `ui/SessionLoading.kt`: "Compartir registros" durante esperas largas.
- `droiddeck-proton-armv80`: progreso real de la descarga. Perfil "Máximo rendimiento seguro".
- Tests: `XboxCloudStatsTest.kt` (+ `XboxCloudNetworkTest`), `DiagnosticsExtrasTest.kt`,
  `test_armv80_download_resume.py` (descarga interrumpida y reanudada contra un servidor local).

## 0016 — `fix`: `x64_exec` sin `X64_HOME` y mensaje de región no disponible
- `droiddeck-steam-x64`: las comprobaciones nuevas no fallan si `X64_HOME` no está definido (corrige la regresión 9).
- `XboxCloudSession.kt` + textos: mensaje claro cuando Microsoft no ofrece ninguna región a la cuenta.
