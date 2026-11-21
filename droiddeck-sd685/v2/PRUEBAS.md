# Resultados de pruebas — DroidDeck 0.7.1-sd685.2 (v2)

Clasificación: ✅ ejecutado aquí · 🧪 emulado (CPU ARMv8.0 emulada) · ⏳ pendiente en tu Redmi Note 13 ·
📐 estimación. Nada de esta tabla está inventado: cada línea tiene su salida en `evidencia/` o en los logs
citados. **No he podido probar la APK en tu teléfono**, así que no afirmo que funcione en él: está
compilada, firmada, verificada y probada en emulación.

## Resumen

| Prueba | Tipo | Resultado |
|---|---|---|
| Compilación `assembleRelease` (v2) | ✅ | `BUILD SUCCESSFUL` (commit `650d3bb`) |
| Verificación de la APK (firma, alineado, assets de sesión, librerías, runtime) | ✅ | Todo OK (`evidencia/verificacion-apk.txt`) |
| Tests Kotlin afectados (perfiles, prefs, ajustes, hilos, xCloud) | ✅ | **31/31** OK (7 nuevos de perfiles) |
| Suite Kotlin completa (`testDebugUnitTest`) | ✅ | **3.867 tests, 0 fallos, 0 errores**, 10 omitidos por el propio proyecto (514 clases; v1: 3.860) |
| Suite Python del proyecto | ✅ | **2.063 OK**, 98 omitidos; 4 fallos **preexistentes** del contenedor (mismos que el original) |
| Tests nuevos `test_armv80_rewrite.py` (8) y `test_armv80_steam.py` | ✅ | OK |
| Recuento de LSE en DroidDeck-Proton 11-12.8 | ✅ | Original **53.158** en 688 archivos → reescrito **0** |
| Atómicas (63 formas, CAS 128 bits, contención) en CPU sin LSE | 🧪 | Original `SIGILL`; reescrito **idéntico** a CPU con LSE |
| `wine` de DroidDeck-Proton en Cortex-A53 (qemu-user y VM con kernel real) | 🧪 | Original error 132; reescrito arranca (`wine cmd`) |
| Programa Windows x86-64 vía FEX ARM64EC (VM Cortex-A53) | 🧪 | **OK** con y sin fsync |
| Programa Windows x86 32 bits vía FEX WoW64 (VM Cortex-A53) | 🧪 | **OK** con y sin fsync |
| `proton run` completo (prefijo de Proton, steam.exe, pantalla virtual) | 🧪 | **OK** x86 (105 s) y x86-64 (117 s) bajo emulación |
| Instalador en el runtime: aplica, marca, es idempotente, rechaza otra base | ✅ | OK (test + prueba de extremo a extremo con la release real: árbol idéntico al validado) |
| Juegos reales, FPS, temperatura, batería en el Redmi Note 13 | ⏳ | Pendiente (ver `OPTIMIZACION.md` §10) |

## Detalle

### Emulación ARMv8.0 (🧪)
- **qemu-user** `-cpu cortex-a53` (sin LSE, estricto) y `-cpu max` (con LSE) para comparar:
  `evidencia/atomics-qemu.txt`.
- **Máquina virtual** `qemu-system-aarch64 -M virt -cpu cortex-a53`, Ubuntu 24.04 arm64, kernel 6.8.
  `/proc/cpuinfo` de la VM: CPU part `0xd03` y *Features* idénticas a las del SD685 (sin `atomics`).
  Salidas: `evidencia/vm-cortex-a53-proton.txt`.
  - `wintest.c` (x86 y x86-64, MinGW): `GetNativeSystemInfo`, `InterlockedCompareExchange/Exchange/
    Increment/Add64`, raíz cuadrada en coma flotante, 4 hilos × 50.000 iteraciones con `CRITICAL_SECTION`,
    1 MB de heap. Esperado y obtenido: `threads 200000 600000 200000 … OK`.
  - Primera ejecución con el script `proton` sin pantalla: x86 se quedó esperando (el escritorio de Wine
    necesita una pantalla). Con Xvfb (como en la sesión real, donde hay gamescope/Xwayland) pasa. Era el
    entorno de la VM, no un fallo.
- Límite: QEMU **no mide rendimiento** (todo va decenas de veces más lento); solo corrección.

### Tests unitarios (✅)
- Kotlin afectados: `PerformanceProfilesTest` 7, `LowTierSessionPrefsTest` 6, `SettingsResetTest` 7,
  `GameThreadHintsTest` 4, `XboxCloudTest` 4, `ModeSettingsLoadingTest` 3 → 31/31.
- Python: `2063 passed, 98 skipped` + fallan `test_cdp_guard` (sin IPv6 en el contenedor),
  `test_pipewire_helper`, `test_vk_external_image_sync`, `test_xclipse_layer` (cabeceras/entorno). Son los
  mismos 4 que fallan con el código original sin modificar en este contenedor (comprobado en la v1).

### APK (✅)
`DroidDeck-0.7.1-sd685.2.apk` — 97.228.749 bytes — SHA-256
`6eaefeaebeebaf45c905f8cf5cdbf1b57cca0231805d20901520f203cf1d5058`. Compilada desde el commit `650d3bb`
de la rama `sd685-optimization` (= `fuentes/`, parches `0001–0012`).

- `package com.droiddeck.launcher.sd685`, `versionName 0.7.1-sd685.2`, `versionCode 19`, `minSdk 26`,
  `targetSdk 28` (como la oficial), `native-code arm64-v8a`, etiqueta "DroidDeck SD685".
- *Authorities* y afinidades con `.sd685` (no choca con la oficial).
- `apksigner verify`: esquemas v2 y v3 válidos; certificado *testkey* de AOSP `a40da80a…5dc`, **el mismo
  que la v1** → Android la acepta como actualización de la v1.
- `zipalign -c -p 4`: OK. `check_session_assets`: OK. `check_android_libraries`: OK.
  `runtime_inputs apk`: OK con los 7 paquetes add-on oficiales fijados (descargados de
  DroidDeck-Components y verificados por SHA-256, los mismos que descargará el teléfono).
- Dentro de la APK: instalador `droiddeck-proton-armv80`, parche `.lse80` (SHA-256 `f81560c5…4390`,
  idéntico al del código), cambios de `droiddeck-session`, `droiddeck-steam-x64` y
  `steam-compatibility`, clases `CpuFeatures`, `LowTierDevice` y `PerformanceProfiles`.
- Frente a la APK oficial 0.7.1: 598 entradas frente a 596; 567 idénticas; 2 nuevas (instalador y
  parche); 29 distintas (código, scripts de sesión, perfiles de arranque, manifiesto y las 15 librerías
  nativas que se compilan localmente, como en la v1).
- Escaneo ARMv8.0 de los 75 ELF ARM64 de la APK: solo `libsyncthingnative.so` (Go) contiene LSE, y Go
  las usa tras comprobar la CPU en tiempo de ejecución; igual en la oficial y en la v1
  (`evidencia/escaneo-isa-apk.txt`).

### Pendiente en el teléfono (⏳)
1. Instalar como actualización de la v1 y abrir una sesión de Steam (debe aparecer el paso de Proton
   ARMv8.0).
2. Un juego de Windows ligero con *DroidDeck-Proton 11-12.8 (ARMv8.0)*; comparar FPS y temperatura con
   `droiddeck-proton-x64`.
3. Perfiles Equilibrado / Rendimiento / Ahorro con el mismo juego.
4. Xbox Cloud con el perfil Xbox Cloud (motor web y nativo).
