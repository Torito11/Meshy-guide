# DroidDeck 0.7.1-sd685.2 (v2) — ultra optimización para Redmi Note 13 (Snapdragon 685 / Adreno 610)

Continúa la v1 (`../`), que se conserva intacta como copia de seguridad. Todas sus reparaciones siguen.

## Lo nuevo en una frase

**Proton ARM64 ya funciona en tu CPU**: reescribí las 53.158 instrucciones atómicas ARMv8.1 de
DroidDeck-Proton por equivalentes ARMv8.0, así que Wine, DXVK y vkd3d corren **nativos** y FEX solo
traduce el código x86 del juego (en la v1 se traducía todo Proton). Además: **7 perfiles de
rendimiento**, sesión a **30 Hz** opcional, pistas de rendimiento de hilos con corte térmico, el cliente
Steam fuera de los núcleos rápidos, y Xbox Cloud ajustado.

## Contenido

| Archivo | Qué es |
|---|---|
| [`OPTIMIZACION.md`](OPTIMIZACION.md) | Informe de optimización: P0 dispositivo, P1 Xbox, P2 Xbox Cloud, P3 Steam/Proton, auditoría, **comparativa antes/después**, cómo medir |
| [`CAMBIOS.md`](CAMBIOS.md) | Registro detallado de cambios v1 → v2, archivo por archivo |
| [`PRUEBAS.md`](PRUEBAS.md) | Resultados de pruebas, separando ejecutadas / emuladas / pendientes / estimadas |
| [`INSTALACION.md`](INSTALACION.md) | Instalación, **actualización desde la v1 conservando datos**, perfiles, volver atrás |
| `apk/` | `DroidDeck-0.7.1-sd685.2.apk` y `SHA256SUMS` |
| `fuentes/` | Código fuente completo de la v2 (`.tar.gz`) |
| `patches/` | `0009–0012`, aplican encima de `../patches/0001–0008` sobre la etiqueta oficial `0.7.1` |
| `evidencia/` | Salidas de las pruebas en CPU ARMv8.0 emulada y el recuento de instrucciones LSE |

## Importante

- **Actualiza la v1 sin borrar datos** (mismo paquete `com.droiddeck.launcher.sd685`, misma firma). No
  puede actualizar el DroidDeck oficial (firmado con la clave privada del proyecto); la oficial no se toca.
- **No la he podido probar en tu teléfono.** Está compilada, firmada, verificada, con tests automáticos y
  probada en una CPU ARMv8.0 emulada con kernel real (Windows x86 y x86-64 bajo Proton: OK). El
  rendimiento real (FPS, temperatura, batería) está **pendiente** de medir en el Redmi Note 13.
- No requiere root, no fuerza frecuencias, no desactiva protecciones térmicas, no elimina funciones.

## Copias de seguridad

- v1: `../apk/DroidDeck-0.7.1-sd685.apk`, `../fuentes/DroidDeck-0.7.1-sd685-src.tar.gz`, `../patches/`.
- Original: `../fuentes/DroidDeck-0.7.1-original-src.tar.gz` y la etiqueta oficial `0.7.1`
  (commit `cdff94e72c45da50af43bbceff28effaf0179caf`).

Licencia GPL-3.0 como el original. Proton y Steam son de Valve; Xbox es de Microsoft; DroidDeck-Proton
es del proyecto DroidDeck. Sin afiliación con ninguno.
