# Registro de cambios — 0.7.1-sd685 (v1) → 0.7.1-sd685.2 (v2)

Base: v1 = upstream `0.7.1` + parches `../patches/0001–0008`. La v2 añade `patches/0009–0012`
(aplican encima de los de la v1). Se conservan **todas** las correcciones de la v1: cliente Steam x86-64
automático en ARMv8.0, herramienta `droiddeck-proton-x64`, 60 Hz en GPU de gama baja, DDFG desactivado
en xCloud de gama baja, paquete propio `com.droiddeck.launcher.sd685`, informe de dispositivo ampliado.

## 0009 — `tools(armv80)`: reescritura de atómicas LSE para CPUs ARMv8.0 (herramienta nueva)

| Archivo | Qué hace |
|---|---|
| `tools/armv80/lse_decode.py` | Decodifica todas las formas LSE: `CAS*`, `CASP*` (registros pares), `LD<op>*` (add, clr, eor, set, smax, smin, umax, umin), `SWP*`, `LDAPR`. Validado contra capstone: 0 discrepancias en 2,4 M de palabras. |
| `tools/armv80/a64.py` | Codificadores A64 (exclusivas `LDXR/STXR/LDXP/STXP`, `LDAR`, ALU, `CSEL`, `MRS/MSR NZCV`, `STP/LDP`, saltos). |
| `tools/armv80/stubs.py` | Genera cada secuencia equivalente ARMv8.0 con el mismo orden de memoria; guarda/restaura registros auxiliares bajo SP y NZCV cuando hace falta; evita los registros reservados de ARM64EC (x13, x14, x18, x23, x24, x28); `CASP` reescribe el par en caso de fallo para conservar la atomicidad. |
| `tools/armv80/rewrite.py` | ELF: convierte un `PT_NOTE` en `PT_LOAD` ejecutable para las secuencias, o si no hay, crea un segmento nuevo que también lleva la tabla de cabeceras movida (`offset == vaddr`, válido en kernels < 5.18). PE: sección nueva `.lse80`, solo rangos ARM64/ARM64EC del *CHPE code map*, que se amplía. |
| `tools/armv80/rewrite_tree.py` | Reescribe un árbol completo y genera el parche `LSE80PATCH1` (zlib, SHA-256 de cada archivo antes y después). |
| `tools/armv80/tests/atomics.c`, `wintest.c` | Pruebas: las 63 formas LSE con contención; programa Windows x86/x64 con atómicas, hilos, FP y heap. |
| `tools/tests/test_armv80_rewrite.py` | 8 tests: decodificación, forma de las secuencias, ELF con/sin `PT_NOTE`, ejecutable con `PT_PHDR`, idempotencia, instalador (aplica y rechaza base distinta). |

## 0010 — `feat(proton)`: instalar DroidDeck-Proton reescrito en CPUs ARMv8.0

| Archivo | Cambio |
|---|---|
| `tools/linuxfs/overlay/usr/local/bin/droiddeck-proton-armv80` (nuevo) | Instalador en el runtime: usa DroidDeck-Proton 11-12.8 ya instalado como base o descarga la release fijada (verifica SHA-256), aplica el parche comprobando cada archivo, crea la herramienta "DroidDeck-Proton 11-12.8 (ARMv8.0)" con marca `.droiddeck-armv80`. Idempotente; no modifica la base. |
| `tools/linuxfs/overlay/usr/local/share/droiddeck-armv80/DroidDeck-Proton-11-12.8.lse80` (nuevo, 787 KB) | El parche (688 archivos, 53.158 instrucciones). |
| `droiddeck-session` | En ARMv8.0 instala/comprueba ese Proton antes de preparar el cliente x86-64; si falla, sigue con `droiddeck-proton-x64`. |
| `droiddeck-steam-x64` | Herramienta por defecto en ARMv8.0: el Proton ARM64 marcado `.droiddeck-armv80`; solo se puentean al cliente x86-64 los Proton ARM64 marcados. |
| `steam-compatibility` | Reconoce las herramientas `-armv80` como destino válido en ARMv8.0. |
| `ProtonMenu.kt` | En ARMv8.0 no se autoinstalan Protons ARM64 sin reescribir (harían `SIGILL`). |
| `SessionFiles.kt`, `app/build.gradle`, `check_session_assets.py`, `.gitattributes` | Empaquetado del instalador y del parche en la APK. |
| `tools/tests/test_armv80_steam.py` | Tests de herramienta por defecto, puenteo y reasignación con `-armv80`. |

## 0011 — `feat`: perfiles de rendimiento, 30 Hz y pistas de hilos fuera del Odin 3

| Archivo | Cambio |
|---|---|
| `core/PerformanceProfiles.kt` (nuevo) | 7 perfiles (Equilibrado, Rendimiento, Ahorro, Compatibilidad, Xbox PC, Xbox Cloud, Steam) que escriben ajustes existentes; detección de "Personalizado". |
| `core/CpuCores.kt` | `littleCores()`: detecta el clúster de eficiencia por frecuencia máxima (SD685 → `0,1,2,3`). |
| `session/SessionPrefs.kt`, `SettingsReset.kt` | Preferencias `performanceProfile`, `pinGamescope`, `gameThreadHintsEverywhere` (incluidas en el restablecimiento). |
| `session/GameThreadHints.kt` | Pistas ADPF también en otros SoC si un perfil lo pide; se detienen en `THERMAL_STATUS_SEVERE` (CRITICAL en el Odin 3). |
| `session/SessionService.kt`, `droiddeck-session` | `BL_CLIENT_PIN_GAMESCOPE=0`: fijar el cliente sin mover gamescope. |
| `ui/ModeSettingsDialog.kt`, `FrontEndActivity.kt` | Selector "Perfil de rendimiento" (pestaña Pantalla) y opción **30 Hz** en *Frecuencia de la sesión*. |
| `stores/xbox/XboxCloudPlayerActivity.kt` | Reproductor web: frecuencia de pantalla según el límite de fps (como el nativo). |
| `res/values{,-es,-b+es+419}/strings.xml` | Textos en inglés y español. |
| `app/build.gradle` | `-PreleaseVersionNameSuffix` para nombrar la build (`0.7.1-sd685.2`). |
| `core/PerformanceProfilesTest.kt` (nuevo) | 7 tests: clúster de eficiencia, valores válidos, cada perfil, ida y vuelta y detección de "Personalizado". |

## 0012 — `fix(hints)`: dejar de pedir pistas que el dispositivo rechaza

`session/GameThreadHints.kt`: si el HAL de energía del teléfono rechaza 5 veces seguidas las sesiones de
pistas para los hilos del juego, el vigilante se detiene en lugar de reintentarlo cada segundo (con una
traza en el registro cada vez).

## Lo que no cambia

- Identificador `com.droiddeck.launcher.sd685`, firma (*testkey*), `versionCode` 19 → actualiza la v1
  conservando datos.
- Ninguna función eliminada. El DroidDeck oficial no se toca.
