# Diagnóstico: Steam se cierra con el error 132 en el Redmi Note 13 (Snapdragon 685)

Fuentes analizadas juntas:

1. El ZIP de diagnóstico `DroidDeck-2026-11-20-02-steam.zip` (sesión del 2026-11-20, 14:43:51–14:44:06).
2. El código fuente de DroidDeck en el commit exacto de tu instalación: `cdff94e` = etiqueta `0.7.1`
   (`device.txt` dice `remote clean · main at cdff94e`; los 80 scripts de sesión de la APK oficial son
   idénticos byte a byte a ese commit).
3. Los binarios reales: el cliente Steam ARM64 de Valve (CDN de Steam), GE-Proton 11-7 aarch64, el
   código de FEX-2610, el rootfs x86 de FEX que usa DroidDeck y la APK oficial 0.7.1.

## 1. Tu hardware, según el propio informe

| Dato | Valor (de `device.txt` y `clocks.log`) |
|---|---|
| Modelo | Xiaomi 23129RA5FL (`sapphire`), placa `bengal`, SoC QTI SM6225 = Snapdragon 685 |
| CPU | 4× Cortex-A73 (hasta 2,80 GHz) + 4× Cortex-A53 (1,90 GHz), **ARMv8.0-A** |
| Extensiones de CPU | `fp asimd evtstrm aes pmull sha1 sha2 crc32 cpuid` → **sin `atomics` (LSE)**, sin `lrcpc`, sin `asimddp`, sin `fphp` |
| GPU | Adreno 610v2 (A6xx de 1.ª generación) |
| RAM | 7,4 GB útiles; 3,5–3,8 GB libres al empezar; 1,8 GB de swap ya en uso |
| Térmica | **SEVERE** ya al empezar la sesión, *headroom* 1,06; núcleos grandes limitados a 2,4 de 2,8 GHz |
| Pantalla | 2400×1080 a 120 Hz; la sesión Steam corría a 1600×720 **a 120 Hz** |

## 2. Qué pasó, paso a paso (`session.log`, `events.jsonl`, `app.log`)

1. `14:43:53` arranca el invitado Linux (proot, runtime `ubuntu-r1-rc5`).
2. `14:43:55` gamescope 3.16.29 **selecciona correctamente** `Turnip Adreno (TM) 610`
   (Mesa 26.3.0-devel, Vulkan 1.3.363). Xwayland y PipeWire arrancan bien.
3. `19:43:57 UTC` "Steam client ready": el cliente **ARM64** de Valve ya estaba descargado.
4. `19:44:01.950` "starting the Steam client" → en el mismo instante:
   `droiddeck-session: line 613: 12101 Illegal instruction ... steam_client` → `== steam exited rc=132`.
5. Como el proceso principal murió, gamescope informa `Primary child shut down!`, Xwayland pierde la
   conexión (`Broken pipe`) y DroidDeck cierra la sesión con `GUEST_EXIT` (status 132) a los ~10 s.

`crash.log` está vacío porque no se colgó ningún proceso Android: la señal la recibió un proceso Linux
dentro de proot.

## 3. Causa raíz del error 132 (demostrada)

- 132 = 128 + 4 → el proceso terminó por **SIGILL (instrucción ilegal)**.
- El proceso era `steamrtarm64/steam`, el **cliente Steam ARM64 nativo de Valve** (no FEX, no Proton,
  no un juego: aún no se había lanzado nada).
- Desensamblé ese cliente (versión 1793740892 del canal `steamdeck_publicbeta`, el que usa DroidDeck).
  `libtier0_s.so`, que todos los hilos de Steam usan al arrancar:

  ```
  ThreadInterlockedIncrement:   mov w1,#1 ; ldaddal w1,w1,[x0] ; ...   ← atomic LSE (ARMv8.1)
  ThreadInterlockedCompareExchange: casal w2,w1,[x0] ; ...              ← atomic LSE (ARMv8.1)
  ```

  No hay ninguna comprobación de la CPU antes. `steamclient.so` contiene **5.888** instrucciones LSE así,
  `steamui.so` 4.470 y el ejecutable `steam` 344 (detalle en `evidencia/steam-arm64-isa.txt`).
- Los Cortex-A73/A53 del Snapdragon 685 implementan ARMv8.0, que **no tiene** esas instrucciones
  (el kernel no anuncia `atomics`). Al ejecutar la primera, la CPU lanza SIGILL. Es determinista: falla
  siempre, en cualquier ajuste.
- Es el mismo fallo del informe #1376 del proyecto (Redmi Note 8, también A73/A53). Los mantenedores
  sospechaban de LSE pero no lo habían comprobado; el desensamblado lo confirma.

**No se puede arreglar dentro del cliente ARM64**: es un binario propietario de Valve compilado para
ARMv8.1 o superior. La solución es no usarlo en esta CPU (ver sección 5).

### Lo que NO es la causa (comprobado)

| Sospecha | Resultado |
|---|---|
| FEX / traducción x86 | No participó: el cliente era ARM64 nativo ("Linux x86 (FEX) not set up"). FEX-2610 **sí** admite tu CPU: su README exige "ARMv8.0-a con FP y CRC32", y sin LSE usa bucles LL/SC (más lento, funciona). DroidDeck lo compila con `-DTUNE_ARCH=armv8-a`. |
| Box64 | DroidDeck no usa Box64 (incluso descarta las variables `BOX64_*`). |
| Turnip / Vulkan / Mesa | gamescope obtuvo el dispositivo Vulkan sin errores. Un fallo de GPU no produce SIGILL. |
| Adreno 610 "fuera del hardware probado" | Es un aviso genérico. Turnip soporta A610 y aquí funcionó. |
| Gamescope | Se cerró *porque* murió Steam (`Primary child shut down`), no al revés. |
| Proton | No se lanzó ningún juego. |
| RAM | Un cierre por memoria sería SIGKILL (137), no SIGILL. Había 3,8 GB libres. |
| Temperatura | Reduce rendimiento pero no provoca instrucciones ilegales. |
| Binarios propios de DroidDeck | Escaneé los 75 ELF ARM64 de la APK: usan *outline atomics* (comprueban la CPU en tiempo de ejecución) → compatibles con ARMv8.0. Por eso gamescope, PipeWire, etc. sí funcionaron. |

## 4. Segundo problema, que habría aparecido después: Proton ARM64

Al arreglar el cliente quedaba otro bloqueo. Para juegos de Windows, DroidDeck usa por defecto un
**Proton ARM64** (el de Valve, GE-Proton aarch64 o DroidDeck-Proton). Comprobé:

- `Makefile.in` de Proton (heredado de Valve, en DroidDeck-Proton): `aarch64_CFLAGS := -march=armv8.2-a -mtune=cortex-x3`.
- GE-Proton11-7-aarch64, desensamblado: `wineserver` (`casal` en `get_shm`), `ntdll.so` (99),
  `ntdll.dll` (244), `kernelbase.dll` (55), DXVK `d3d11.dll` (11.484) — todas sin comprobación
  (`evidencia/ge-proton-aarch64-isa.txt`).

Es decir: **cualquier juego de Windows lanzado con Proton ARM64 también moriría con SIGILL en tu CPU.**
Además, en modo cliente x86-64 DroidDeck descargaba automáticamente GE-Proton aarch64 (~650 MB) que nunca
podría ejecutarse.

## 5. Por qué el cliente x86-64 sí puede funcionar

DroidDeck ya trae un modo "cliente Steam x86-64 (experimental)": el cliente x86 de Valve corre bajo
**FEX**, que traduce x86 a instrucciones ARMv8.0. El propio script ya evitaba el *web helper* ARM64 en
CPUs sin `atomics`. Faltaba:

1. Elegirlo automáticamente en CPUs ARMv8.0 (hoy hay que descubrir el ajuste tras el fallo).
2. No enviar los juegos de Windows a Proton ARM64. Bajo proot, el contenedor *Steam Linux Runtime* de
   Valve no tiene *namespaces* (por eso DroidDeck ya ejecuta los juegos Linux "sin contenedor" con
   `droiddeck-direct`). Comprobé que el rootfs x86 de FEX que usa DroidDeck (Ubuntu 24.04,
   sha256 `2854b06d…`) trae `python3.12` y las librerías x86_64/i386 que necesita Proton.

## 6. Otros hallazgos del registro

| Observación | Valoración |
|---|---|
| Sesión a **120 Hz** con el teléfono en térmica SEVERE | Ni la interfaz de Steam ni los juegos pueden llegar a 120 fps en esta GPU; componer a 120 Hz solo duplica trabajo y calor. → límite a 60 Hz en gama baja (ajustable). |
| Núcleos grandes ya limitados a 2,4 GHz antes de jugar | *Throttling* térmico activo desde el inicio. Recomendaciones en `INSTALACION.md`. |
| `qdgralloc: No map for format 0x38/0x3b` | Sondeos de formatos (R8 y R10G10B10A10) en búferes de 4×4; el compositor cae al formato soportado ("screen output 2400x1080, 5 buffers"). Inofensivo. |
| `No CAP_SYS_NICE`, `Failed to add waitable: Operation not permitted` | Normal en el sandbox de Android (sin tiempo real). |
| Errores de D-Bus de PipeWire/WirePlumber | Ocurren antes de que exista el bus de sesión; luego "session bus up". Normal. |
| `avc: denied` de propiedades `vendor_soc_*` y sysfs de KGSL | SELinux para apps sin privilegios; DroidDeck usa alternativas (contador de ciclos para el reloj de GPU). Inofensivo. |
| 3,5 GB de RAM libres | Suficiente para el cliente; el cliente x86-64 bajo FEX consume más que el ARM64. zRAM de DroidDeck ya está activo. |

## 7. Límites físicos del Snapdragon 685 (honestamente)

- **CPU**: un A73 a 2,4–2,8 GHz rinde aproximadamente como un PC de gama baja de hace ~10 años; con la
  traducción de FEX (sin LSE ni RCPC, la emulación del modelo de memoria TSO de x86 es más cara) se pierde
  bastante más. El cliente Steam x86-64 y su interfaz web irán lentos.
- **GPU**: la Adreno 610 es una GPU de entrada (~1/5–1/6 de una Adreno 650). Juegos 3D modernos no son
  realistas; juegos 2D, indies ligeros y títulos antiguos sí son candidatos.
- **No existe** un ajuste o controlador que añada LSE a la CPU: es una limitación del silicio.
