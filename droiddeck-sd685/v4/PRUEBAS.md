# Resultados de pruebas — DroidDeck 0.7.1-sd685.4 (v4)

**Separación clara**: todo lo de las secciones A–C se ejecutó **en el contenedor de desarrollo** (un PC
x86-64 en la nube, sin tu teléfono). La sección D es lo que **solo tu Redmi Note 13 puede probar** y está
pendiente. **No he instalado esta APK en tu teléfono**; compilar bien no es probar en el teléfono.

## A. Pruebas automáticas del proyecto (contenedor)

| Prueba | Resultado |
|---|---|
| Suite Python completa (`tools/tests`) | **2.108 OK**, 98 omitidas por el proyecto, **3 fallos preexistentes** del contenedor (PipeWire, sincronización Vulkan externa, capa Xclipse: fallan igual en la v3 y en el original), 1 excluida (IPv6, el contenedor no tiene IPv6). v3: 2.080 OK |
| Watchdog y OpenGL (`test_steam_first_frame_watch.py`, **36**, reescrito) | Todo con `set -eu` como en el teléfono y con **tus líneas de registro reales**. Comprueba: el watchdog **sobrevive a `set -e`** (regresión de la v3); fallo de OpenGL del compositor → reinicio **único** con OpenGL por software **verificado**; **2 reinicios del ayudante** se detectan sin que muera el cliente; si el software tampoco funciona no se reinicia y con **4 reinicios se detiene Steam** (sin bucle); en modo software también se detiene a los 4; reinicios y errores de arranques anteriores no cuentan (23 reinicios previos como en tu registro); registro rotado por Steam; sin `glxinfo` se decide por observación y el límite sigue aplicando; primer fotograma → no se toca nada; cliente parado; biblioteca que falta; decisión de OpenGL: GPU que funciona se mantiene, el fallo de tu teléfono pasa a software, ninguno → `none`, caché por FEX/rootfs/controlador, sin pantalla o sin glxinfo no se decide, sin *thunks* solo software, una comprobación colgada cuenta como fallo, **glxinfo que sale con 0 sin crear contexto cuenta como fallo**; `x64_exec` arranca el cliente con el entorno y las opciones correctas en cada caso; la reparación no re-descarga por una causa de OpenGL |
| Instalador Proton ARMv8.0 (`test_armv80_install_base.py`, **5**, nuevo) | Base con `d3d12.dll` cambiado → **no se copia**, se usa la versión original y la herramienta del usuario queda intacta; otro archivo cambiado → se detecta al parchear y se usa la original **en el mismo inicio**; base intacta → sin descarga; tras una descarga fallida no se vuelve a copiar la base; ya instalado → sin trabajo |
| Pruebas de los 40 archivos que tocan los scripts cambiados | **328 OK** |
| Kotlin: pruebas afectadas | **72 OK, 0 fallos** (`LoadingStepExplainedTest` 6, `Armv80ProtonComponentsTest` 1, `DiagnosticsExtrasTest`, `EnhancedSessionLogShareTest`, `ComponentUpdatesTest`, `PowerVrQueuedComponentsTest`, `LoadingStateTest`) |
| Kotlin: suite completa (`testDebugUnitTest`, 520 clases) | **3.889 pruebas, 0 fallos, 0 errores**, 10 omitidas por el proyecto (v3: 3.886) |

## B. Compilación y verificación de la APK (contenedor)

| Prueba | Resultado |
|---|---|
| `assembleRelease` | **BUILD SUCCESSFUL**, commit `65bf8f1` |
| Paquete / versión | `com.droiddeck.launcher.sd685`, `0.7.1-sd685.4`, `versionCode` 19 (igual que v1–v3) |
| Firma | v2+v3, **mismo certificado** que v1/v2/v3 (`a40da80a…5dc`) → se actualiza sin perder datos |
| `zipalign`, `check_session_assets`, `runtime_inputs apk` (con los 7 paquetes oficiales fijados, colocados solo para verificar), `check_android_libraries` | OK |
| Cambios presentes dentro de la APK | **39 comprobaciones OK, 0 faltan** (funciones nuevas en los scripts, los 7 textos nuevos en en/es/es-419); el `droiddeck-steam-x64` de la APK es idéntico byte a byte al del código |
| Claves | `SGDB_API_KEY` vacío (no se incrusta la clave de la APK oficial) |
| Escaneo ARMv8.0 de los 75 ELF ARM64 | Igual que la v3: solo `libsyncthingnative.so` (Go, comprueba la CPU por sí mismo) |

## C. Experimentos con los componentes reales de tu teléfono (contenedor)

Detalles y salidas en `evidencia/`.

| Experimento | Resultado |
|---|---|
| Rootfs x86 Ubuntu 24.04 que descarga tu teléfono (SHA-256 `2854b06d…a178` verificado), `glxinfo -B` con la configuración de software de la v4, en x86 nativo | **Crea contexto OpenGL 4.6** `llvmpipe (LLVM 20.1.8)`, Mesa 26.1.6 |
| Mismo rootfs con zink sin Vulkan (fallo al estilo de tu teléfono) | Mismos mensajes que tus registros (`ZINK: vkCreateInstance failed`, `failed to load driver: zink`); **glxinfo sale con 0 aunque falle** → la v4 exige el *renderer* |
| Cliente Steam x86-64 real `1795048523` (el de tu teléfono) con la configuración de software de la v4, x86 nativo, sin FEX | Detecta `llvmpipe` como GPU, arranca su ayudante web sin GPU y **sin ningún error de OpenGL**, y dibuja sus propias ventanas (`evidencia/contenedor-steam-opengl-software.png`) |
| Mismo cliente con OpenGL roto | Mismos errores de Mesa que tu teléfono; aquí el cliente aborta antes (`glXChooseVisual failed`): en tu teléfono sí hay visuales GLX y el fallo es al crear el contexto |
| **Menú de Steam** en el contenedor | **No alcanzado**: sin internet directo para Steam y con su conexión interna cliente–ayudante rechazada por el entorno (error 0x3009). **No demuestra nada sobre tu teléfono** en ningún sentido |
| VM ARMv8.0 (Cortex-A53 emulado: `CPU part 0xd03`, sin `atomics`, mismas *Features* que el SD685), dentro del **runtime Linux de DroidDeck** (Ubuntu 26.04, glibc 2.43, Mesa 26.0.8+droiddeck1, SHA-256 verificado), con **tu FEX 2611-r10** (SHA-256 verificado) y **tu rootfs x86** | GPU por *thunks* (zink, con las variables de tu teléfono): **falla** como en tu teléfono. llvmpipe ARM por *thunks* (vía alternativa que probé): **`glxinfo` se cae** (`GLXBadFBConfig`) → descartada. llvmpipe x86 bajo FEX: **contexto OpenGL 4.6 creado**. **Funciones reales de la v4** (`x64_gl_try`/`x64_gl_mode`, el mismo archivo que va en la APK): deciden **`software`** y lo guardan (72 s en CPU emulada; en el teléfono será bastante menos). `evidencia/vm-armv80-opengl-fex.txt` |

## D. Pendiente en tu Redmi Note 13 (⏳, no probado)

- Que la comprobación de OpenGL dé `software` (o `gpu`) en tu teléfono, y cuánto tarda.
- **Que el menú de Steam aparezca** con OpenGL por software, y con qué fluidez.
- Que, si no aparece, el watchdog lo explique y detenga Steam a los 4 reinicios (sin bucle).
- La descarga única de la versión original del Proton ARMv8.0 y su instalación; juegos con él.
- Todo lo pendiente de la v3 (tiempos reales, Xbox Cloud con tu cuenta, perfiles, temperatura, batería).

## Errores encontrados por las pruebas durante esta versión

1. `test_steam_x64_cpu.py` (9 pruebas) falló tras mis cambios: `ROOTFS_SHA256: unbound variable` con `set -u`.
   Corregido sin tocar esas pruebas; vuelven a pasar.
2. Mis pruebas nuevas de `x64_exec` se bloqueaban: el `tail --pid` que deja `x64_exec` esperaba a un proceso
   zombi que Python no recoge mientras lee las tuberías. Era un artefacto de la prueba (en el teléfono la
   salida va a un archivo); la prueba ahora usa archivos como el lanzador.
3. Al probar con el rootfs real descubrí que `glxinfo` sale con 0 cuando no crea contexto; la comprobación ya
   exigía el *renderer*, y lo cubre una prueba nueva.
4. En la VM ARMv8.0, Mesa repetía cada error 9 veces y llenaba el registro de la decisión de OpenGL: ahora cada
   error distinto aparece una vez (parche `0021`), y lo volví a comprobar en la VM con el código final.
5. Sin relación con la APK: una ejecución de la suite Kotlin se cortó por falta de memoria del contenedor
   mientras la VM estaba encendida; se repitió con la VM apagada (resultado en la tabla A). Y mi script de
   verificación marcó un "falta" falso por un `$0` sin escapar en el texto buscado; lo comprobé a mano.
