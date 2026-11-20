# Informe de pruebas

Fecha: 2026-11-20. Entorno: contenedor Linux x86_64 (sin teléfono conectado, sin KVM). Herramientas:
JDK 21, Gradle 8.10.2 (wrapper del proyecto), AGP 8.8.0, Android SDK 34/35, build-tools 35.0.0,
NDK 27.3.13750724, CMake 3.22.1, Rust 1.97 + cargo-ndk 4.1.2.

## Resumen

| Prueba | Resultado |
|---|---|
| Causa raíz del SIGILL en el binario real de Valve | ✅ Demostrada (desensamblado) |
| Compilación de referencia sin cambios funcionales vs APK oficial | ✅ 596/596 archivos, 576 idénticos byte a byte |
| Compilación final `assembleRelease` | ✅ `BUILD SUCCESSFUL` |
| Firma y alineación | ✅ v2+v3 válidas (testkey AOSP), zipalign OK |
| Paquete / etiqueta / *authorities* propios (convive con la oficial) | ✅ |
| Comprobaciones de release del proyecto | ✅ `check_session_assets`, `runtime_inputs apk`, `check_android_libraries` |
| Cambios presentes dentro de la APK | ✅ 3 scripts + 2 clases nuevas verificadas |
| Compatibilidad ARMv8.0 de los 75 ELF ARM64 | ✅ Sin atomics LSE sin protección (ver nota de Go en `evidencia/LEEME.md`) |
| Parches → árbol idéntico al modificado | ✅ mismo hash de árbol `220aa166…` (antes del parche de documentación) |
| Tests Python del proyecto (2.127) | ✅ Todos los relacionados pasan; 4 fallos ajenos al cambio (ver abajo) |
| Tests nuevos (Python 14, Kotlin 13) | ✅ Todos pasan |
| Tests Kotlin dirigidos (39) | ✅ Todos pasan |
| Suite Kotlin completa | ver sección 4 |
| Instalar y abrir en un teléfono/emulador | ❌ **No realizado**: sin dispositivo y sin KVM |
| Steam x86-64 / Proton x86-64 / Xbox en el Redmi Note 13 | ❌ **No verificado en el dispositivo** |

## 1. Verificación de la causa raíz

- Descargué el cliente Steam ARM64 del CDN de Valve (canal `steamdeck_publicbeta`, versión 1793740892,
  el que instala DroidDeck) y lo desensamblé: `ThreadInterlockedIncrement` = `ldaddal` sin comprobación
  previa; 5.888 atomics LSE en `steamclient.so`. Tu CPU no anuncia `atomics` → SIGILL determinista.
- GE-Proton11-7-aarch64 y el `Makefile.in` de Proton: ARMv8.2 / LSE sin protección.
- FEX-2610: requisito oficial ARMv8.0 + FP + CRC32; sin LSE usa LL/SC.
- Rootfs x86 de FEX usado por DroidDeck (sha256 verificado): contiene `python3.12` y librerías
  x86_64/i386 necesarias para Proton.

## 2. Reproducibilidad del pipeline

Para no depender de Docker (el pipeline oficial compila con él varios componentes nativos), los
componentes **no modificados** se toman de la APK oficial 0.7.1, que procede del mismo commit; los
paquetes add-on y el componente Venus se descargan y verifican por SHA-256 como hace el CI.

Prueba de control: compilé el código **sin** mis cambios funcionales con este pipeline. Resultado frente
a la APK oficial: mismos 596 archivos; 576 idénticos; diferencias solo en `classes*.dex` (etiqueta de
build y BuildConfig), perfiles de arranque, `version-control-info` y 15 librerías nativas compiladas
localmente con el NDK/Rust (`evidencia/reproducibilidad-build-referencia.txt`).

## 3. APK final

`DroidDeck-0.7.1-sd685.apk` — 96.552.771 bytes —
SHA-256 `6fa6e71d80e759e717edeb751101c035b551099de1103bc51b048498e0965914`.
Compilada desde el commit `09d50aa` de la rama `sd685-optimization` (el parche 0008 posterior solo añade
documentación).

- `package: com.droiddeck.launcher.sd685`, `versionName 0.7.1-sd685`, `versionCode 19`,
  `minSdk 26`, `targetSdk 28` (como la oficial), `native-code: arm64-v8a`, etiqueta "DroidDeck SD685".
- Todas las *authorities* y afinidades llevan `.sd685` → no choca con la app oficial instalada.
  (La entrada `org.khronos.openxr.runtime_broker` está dentro de `<queries>`, no es un proveedor.)
- `apksigner verify`: v2 y v3 válidas, certificado testkey AOSP (`a40da80a…`). v1 no se usa porque
  `minSdk ≥ 24` (igual que la oficial).
- Frente a la APK oficial: 567 archivos idénticos; difieren el manifiesto (paquete), `classes*.dex`
  (código modificado), `resources.arsc` y `cq.xml` (cadenas nuevas → IDs de recurso), los 3 scripts
  modificados, perfiles y las 15 `.so` compiladas localmente. Ningún archivo falta ni sobra.
- Detalle completo: `evidencia/verificacion-apk.txt`.

## 4. Tests automáticos

### Tests nuevos

- `tools/tests/test_armv80_steam.py` (14): detección ARMv8.0 en `droiddeck-session`; herramienta por
  defecto (`droiddeck-proton-x64` en ARMv8.0, la de siempre en CPUs con LSE o sin datos); eliminación de
  puentes ARM64 y escritura de la herramienta directa; el ejecutor lanza Proton con el verbo correcto y
  explica qué instalar si falta; reasignación de títulos en `steam-compatibility`.
- `CpuFeaturesTest` (7): lectura de `AT_HWCAP` de auxv, `/proc/cpuinfo` real del Snapdragon 685,
  token exacto `atomics`, núcleos heterogéneos, prioridad auxv > cpuinfo, clasificación de gama baja.
- `LowTierSessionPrefsTest` (6): cliente efectivo, 60 Hz por defecto, límite combinado, DDFG de xCloud
  respetando elecciones guardadas, restablecimiento de ajustes.

### Tests existentes del proyecto

- **Python (2.127 tests)**: todos los relacionados con Steam/compatibilidad/FEX pasan. Fallan 4, los
  mismos 4 que en el código original sin modificar en este contenedor: `test_cdp_guard` (sin IPv6),
  `test_pipewire_helper` (entorno), `test_vk_external_image_sync` y `test_xclipse_layer` (faltan cabeceras
  de Vulkan). Comprobado ejecutándolos sobre el árbol original.
- **Kotlin dirigidos (39)**: `CpuFeaturesTest`, `LowTierSessionPrefsTest`, `DeviceReportCpuTest`,
  `SettingsResetTest`, `XboxCloudTest`, `SessionLaunchFailureTest`, `CoreAllocationPrefsTest`,
  `SessionScalingPrefsTest`: todos pasan.
- **Kotlin, suite completa**: RESULTADO_SUITE_KOTLIN

## 5. Lo que NO se pudo probar (y por qué)

- **Instalación y arranque en Android**: no hay teléfono conectado a esta sesión y el contenedor no tiene
  KVM, sin el cual el emulador de Android no arranca imágenes x86_64 (y no ejecuta imágenes ARM64 en un
  host x86).
- **Steam x86-64 bajo FEX en tu CPU**: la ruta existe en DroidDeck desde antes y los mantenedores la
  usaron en otros dispositivos, pero no en un ARMv8.0.
- **`droiddeck-proton-x64`**: es nueva; ejecutar Proton x86-64 sin contenedor bajo FEX es una técnica
  conocida, pero no está probada en DroidDeck ni en tu teléfono.
- **Rendimiento real (FPS, temperatura, RAM)**: requiere el dispositivo.

## 6. Cómo validarlo en tu teléfono

1. Instala la APK (ver `INSTALACION.md`), instala el runtime y pulsa Play.
2. En `session.log` deberías ver `== cpu: ARMv8.0 without LSE atomics ...` y
   `starting the x86-64 SteamRT3 client under FEX` en lugar del cliente ARM64.
3. Si algo falla, usa **Compartir registros** en la app: el nuevo `device.txt` incluye "CPU class",
   "Steam client" y "Session refresh cap", útiles para diagnosticar.
