# DroidDeck 0.7.1-sd685.3 (v3) — Redmi Note 13 (Snapdragon 685 / Adreno 610)

Continúa la v2 (`../v2`) y la v1 (`../`), que se conservan intactas como copia de seguridad. Todas sus
reparaciones siguen (cliente Steam x86-64 en ARMv8.0, Proton ARM64 reescrito para tu CPU, perfiles, 60/30 Hz).

## Lo nuevo

1. **Bloqueo "Esperando el primer fotograma de Steam"**: el código ya sabía que el menú de Steam (un
   Chromium x86 bajo FEX usando la GPU) puede rendirse y dejar la pantalla vacía para siempre, pero solo lo
   anotaba. Ahora una vigilancia lo detecta y **reinicia Steam una vez con renderizado por software**
   (recordado para esa versión del cliente), detecta un cliente parado y **explica en pantalla** qué hace
   Steam mientras arranca. Tras 90 s puedes **Compartir registros** sin cancelar.
2. **Arranque de Steam más rápido**: se dejan de rehacer en cada inicio cientos de enlaces del runtime y un
   `ldconfig` x86 bajo FEX (medido en contenedor: 5,9 s → 9 ms), no se re-verifica una versión del cliente que
   ya funcionó, y el Proton ARMv8.0 instalado se comprueba sin arrancar Python.
3. **Tiempos de inicio medidos** (apertura de la app, Linux, FEX, Steam, juego → primera imagen → fluido),
   primer inicio aparte de los siguientes, en el ZIP de registros.
4. **Xbox Cloud**: región por **menor latencia medida** entre las regiones oficiales de tu cuenta (solo si gana
   de verdad), **calidad automática** según las pérdidas medidas, y **sección de estadísticas reales**
   (resolución, fps, códec, latencia, jitter, pérdidas, bitrate, decodificación, región, estado).
5. **Descargas**: progreso real de la descarga del Proton ARMv8.0 y reanudación comprobada.
6. Perfil "**Máximo rendimiento seguro**".

## Contenido

| Archivo | Qué es |
|---|---|
| [`CAMBIOS.md`](CAMBIOS.md) | Lista completa de cambios y **errores encontrados y corregidos** |
| [`TIEMPOS.md`](TIEMPOS.md) | **Comparación de tiempos antes/después** (lo medido y cómo medirlo en tu teléfono) |
| [`PRUEBAS.md`](PRUEBAS.md) | Resultados de pruebas: qué se probó y qué no |
| [`INSTALACION.md`](INSTALACION.md) | Instalación/actualización sin perder datos, qué verás, cómo enviarme registros |
| [`LIMITACIONES.md`](LIMITACIONES.md) | **Limitaciones conocidas** y **recomendaciones** de mejoras futuras |
| `apk/` | `DroidDeck-0.7.1-sd685.3.apk` y `SHA256SUMS` |
| `fuentes/` | Código fuente completo de la v3 |
| `patches/` | `0013–0016` (encima de `../v2/patches/0009–0012` y `../patches/0001–0008`) |
| `evidencia/` | Mediciones y salidas de pruebas |

## Importante

- **No la he probado en tu Redmi Note 13.** Compilación correcta no es lo mismo que funcionamiento: está
  compilada, firmada, verificada y con pruebas automáticas (incluidas pruebas de recuperación con procesos
  reales y de reanudación de descargas), pero el comportamiento en el teléfono está pendiente.
- **Necesito tus registros del bloqueo de Steam** para confirmar la causa (ver `LIMITACIONES.md`).
- **Xbox Cloud en Colombia**: no he podido confirmar desde aquí su disponibilidad oficial; DroidDeck usa lo
  que Microsoft responde para tu cuenta y no simula nada.
- Actualiza la v1/v2 **sin borrar datos** (mismo paquete y firma). No requiere root, no fuerza frecuencias,
  no desactiva protecciones térmicas, no elimina funciones.
