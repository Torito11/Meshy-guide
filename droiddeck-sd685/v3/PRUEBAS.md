# Resultados de pruebas — DroidDeck 0.7.1-sd685.3 (v3)

✅ ejecutado aquí · 🧪 emulado · ⏳ pendiente en tu Redmi Note 13. **Compilar bien no es probar en el
teléfono**: no he podido instalar la APK en tu dispositivo, así que nada de esto afirma que funcione allí.

## Resumen

| # (tu lista) | Prueba | Tipo | Resultado |
|---|---|---|---|
| 1–4 | Análisis del proyecto, problemas, causas, correcciones | ✅ | Ver `CAMBIOS.md` (9 errores, incluida 1 regresión mía detectada y corregida) |
| 5 | Funciones anteriores siguen funcionando | ✅ | Suite Kotlin completa **3.886 tests, 0 fallos, 0 errores** (10 omitidos por el proyecto; v2: 3.867) · Suite Python **2.080 OK**, 98 omitidos, 4 fallos **preexistentes** del contenedor (IPv6, PipeWire, cabeceras Vulkan/Xclipse: fallan igual en el código original) |
| 6 | Compilación | ✅ | `assembleRelease` **BUILD SUCCESSFUL**, commit `6462186` |
| 6 | Verificación de la APK | ✅ | Firma v2+v3 con el **mismo certificado** que v1/v2 (`a40da80a…5dc`), `zipalign` OK, `check_session_assets` OK, `runtime_inputs apk` OK (con los 7 paquetes oficiales fijados), `check_android_libraries` OK, todos los cambios presentes (`evidencia/verificacion-apk.txt`) |
| 7 | Tiempos de inicio disponibles | ✅ | Enlaces del runtime **5.899 → 9 ms** (143 ms al rehacerlos); comprobación del Proton ARMv8.0 **41 → 5 ms**. Medido en contenedor (`TIEMPOS.md`); en el teléfono ⏳ |
| 7 | Cálculo de tiempos desde los registros | ✅ | `StartupTimesTest` (4): fases a partir de `events.jsonl` + `== STEP`, medianoche, primer inicio, historial |
| 8 | Descargas y reanudación | ✅ | `test_armv80_download_resume.py`: descarga cortada a mitad contra un servidor local con rangos → la segunda **solo pide el resto** (Range > 0) y el archivo final es **idéntico** (SHA-256); se emite el progreso |
| 9 | Registros | ✅ | `DiagnosticsExtrasTest` (2): `timings.txt` también para un arranque que no llegó a la pantalla, `memory.txt` |
| 10 | Funciones de Xbox Cloud accesibles | ✅ | `XboxCloudStatsTest` (6): estadísticas desde informes WebRTC (incluido el formato del reproductor web), calidad, historial, límite automático · `XboxCloudNetworkTest` (3): elección de región (solo con ventaja ≥ 15 ms y ≥ 15 %), regiones sin respuesta, mediana/variación · **Streaming real** ⏳ (necesita tu cuenta y tu red) |
| 11 | Recuperación de Steam | ✅ | `test_steam_first_frame_watch.py` (13), **con procesos reales**: fallo de GPU del menú → cliente detenido + marca de software + reinicio pedido; errores de GPU de un arranque anterior no cuentan; primer fotograma → se deja el cliente en paz y se recuerda la versión; cliente parado en GPU → reinicio en software; parado en software → solo aviso; progreso cada pocos segundos; biblioteca que falta; la sesión reinicia **una sola vez**; marcas borradas al empezar; nueva versión del cliente → vuelve a probar la GPU · `LoadingStepExplainedTest` (4): mensajes traducidos |
| 12 | Qué se probó y qué no | — | Este documento |

## No probado (⏳ en tu teléfono)

- Que el bloqueo de Steam de tu teléfono sea el fallo de GPU del menú (causa probable según el código).
- Arranque real de Steam x86-64 bajo FEX con `-noverifyfiles`, y su tiempo.
- Juegos reales con el Proton ARMv8.0 (la v2 lo probó en CPU emulada: Windows x86 y x86-64 OK).
- Xbox Cloud con tu cuenta: disponibilidad en Colombia, regiones que Microsoft te ofrece, calidad y latencia.
- Perfiles, temperatura y batería.

## Errores de esta versión detectados por las pruebas

- 9 tests de `test_steam_x64_cpu.py` fallaron tras mis cambios en `x64_exec` (`X64_HOME` sin definir con
  `set -u`). Corregido sin modificar esos tests; vuelven a pasar.
- Una APK intermedia salió de 183 MB porque incluía los paquetes add-on que había descargado para la
  verificación de la v2. Se apartaron y se recompiló: 97,3 MB, sin paquetes (se descargan y verifican en el
  teléfono, como en la oficial).
