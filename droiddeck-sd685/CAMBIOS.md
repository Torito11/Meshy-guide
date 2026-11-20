# Registro de cambios: DroidDeck 0.7.1 → 0.7.1-sd685

Base: DroidDeck **0.7.1** (etiqueta `0.7.1`, commit `cdff94e72c45da50af43bbceff28effaf0179caf`), la misma
versión que tienes instalada. Rama de trabajo: `sd685-optimization`. Los parches completos están en
`patches/` (se aplican con `git am`).

## Correcciones funcionales

### 1. El cliente Steam ARM64 ya no se usa en CPUs ARMv8.0 (causa del error 132)

| Archivo | Cambio |
|---|---|
| `app/.../core/CpuFeatures.kt` (nuevo) | Detecta LSE leyendo `HWCAP_ATOMICS` de `/proc/self/auxv` (lo que el kernel anuncia), con `/proc/cpuinfo` de respaldo. Tres estados: presente, ausente, desconocido. Solo "ausente" cambia el comportamiento. |
| `app/.../session/SessionPrefs.kt` | `steamClientArch()` devuelve `x86_64` siempre que la CPU carece de LSE, aunque hubiera guardado `arm64`. |
| `app/.../ui/ModeSettingsDialog.kt` | En esas CPUs, Ajustes de Steam → Cliente de Steam ofrece solo x86-64 y explica por qué. |
| `app/.../SessionActivity.kt` | Si aun así se produce un SIGILL con el cliente ARM64 en una CPU ARMv8.0, el mensaje explica la causa real (antes: "puede ser un problema de compatibilidad... comparte los registros"). |
| `app/.../FrontEndActivity.kt` | El estado de la interfaz refleja el cliente efectivo. |

### 2. Los juegos de Windows ya no se envían a Proton ARM64 en CPUs ARMv8.0

| Archivo | Cambio |
|---|---|
| `tools/linuxfs/overlay/usr/local/bin/droiddeck-steam-x64` | En CPUs sin LSE: no crea los puentes a Proton ARM64 (y borra los existentes); escribe la herramienta **`droiddeck-proton-x64`**, que ejecuta el Proton x86-64 de Valve (Experimental; si no, 10.0/9.0/8.0) directamente bajo FEX, sin el contenedor Steam Linux Runtime (bajo proot no tiene *namespaces*), con el mismo entorno de GPU que `droiddeck-direct`; la marca como predeterminada; y pide al cliente instalar Proton Experimental (`steam://install/1493710`) si no hay ninguno. En CPUs con LSE se elimina esa herramienta y todo sigue como antes. |
| `tools/linuxfs/overlay/usr/local/bin/steam-compatibility` | `x64_repoint`: con `droiddeck-proton-x64` como destino también mueve los títulos que apuntaban a un puente ARM64 eliminado. Con cualquier otro destino, regla original intacta. |
| `tools/linuxfs/overlay/usr/local/bin/droiddeck-session` | Registra en `session.log` cuando la CPU es ARMv8.0; en ese caso no descarga GE-Proton aarch64 (~650 MB inútiles) ni actualiza las piezas del cliente ARM64 que no puede ejecutar. |

### 3. Perfil de gama baja (Snapdragon 685 / Adreno 610)

`LowTierDevice` (nuevo): CPU ARMv8.0 **o** Adreno 605–620. Solo cambia **valores por defecto**; todo
sigue siendo ajustable.

| Archivo | Cambio |
|---|---|
| `SessionPrefs.kt`, `SessionActivity.kt` | Nuevo límite de frecuencia de la sesión (`refreshCap`): **60 Hz por defecto en gama baja**, máximo del panel en el resto. Se aplica al elegir el modo de pantalla y al ritmo del compositor/gamescope. |
| `ModeSettingsDialog.kt`, `FrontEndActivity.kt` | Ajuste "Frecuencia de la sesión" (60 Hz / máximo del panel) en la pestaña Pantalla. |
| `SettingsReset.kt` | "Restablecer ajustes" también lo restablece. |
| `stores/xbox/XboxCloudSettings.kt` | Xbox Cloud, motor nativo: DDFG desactivado por defecto en gama baja. Una elección guardada se respeta. |

### 4. Diagnóstico

`DeviceReport.kt`: el `device.txt` de los registros incluye ahora "CPU class" (p. ej. "ARMv8.0 (no LSE
atomics): Valve's arm64 Steam client and arm64 Proton cannot run"), "Low-tier defaults", el cliente Steam
efectivo y el límite de refresco.

### 5. Textos

Cadenas nuevas en inglés (base), **español de España** (`values-es`) y **español de Latinoamérica**
(`values-b+es+419`). Los demás idiomas muestran el texto en inglés.

## Cambios de compilación (no afectan al comportamiento)

| Archivo | Cambio |
|---|---|
| `tools/sd685/stage_release_inputs.sh` (nuevo) | Coloca en las rutas generadas (ignoradas por git) los componentes nativos **no modificados** de la APK oficial 0.7.1, que el pipeline oficial genera con Docker; descarga y verifica por SHA-256 los paquetes add-on y el componente Venus fijados, igual que el CI. |
| `tools/sd685/addon-packs-0.7.1.properties` (nuevo) | Hashes de los paquetes add-on de la release 0.7.1 (proot, directaudio, tracking, **xbox**, comet, butler, powervr) para que la app descargue y verifique exactamente los mismos. |
| `app/build.gradle` | Opciones `-PaddonPackPins` y `-PreleaseApplicationIdSuffix` (paquete y nombre propios para una build no firmada por el proyecto). |
| `app/src/main/AndroidManifest.xml` | La etiqueta de la app usa un *placeholder* (por defecto `@string/app_name`, sin cambios en la build normal). |

## Lo que NO se cambió

- Ningún componente de terceros se sustituyó: gamescope, Mesa/Turnip, FEX, PulseAudio, Proton y los
  paquetes add-on son exactamente los de la release 0.7.1.
- No se eliminó ninguna función (Xbox, tiendas, escritorio, VR, gafas, etc.).
- No requiere root ni modifica Android.
- Versión: `0.7.1-sd685` (versionCode 19), paquete `com.droiddeck.launcher.sd685`.
