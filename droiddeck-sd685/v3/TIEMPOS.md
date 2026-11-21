# Tiempos de inicio — antes y después

**Lo que se ha medido aquí está medido en el contenedor de compilación (x86-64 rápido, sin proot ni FEX).**
En tu Redmi Note 13 cada proceso cuesta bastante más (proot intercepta llamadas al sistema y los A53/A73 son
más lentos), así que los valores absolutos allí serán **mayores**. La proporción de la mejora es lo
comparable. **No he medido nada en tu teléfono** y no invento esos números.

## Medido (contenedor)

| Paso de cada arranque de Steam en tu CPU | v2 (antes) | v3 (ahora) | Nota |
|---|---|---|---|
| Enlaces de bibliotecas del runtime de Valve (800 enlaces simulados, con poda frente al rootfs) | **5.899 ms** cada arranque | **9 ms** si nada cambió · **143 ms** si hay que rehacerlos | Además se evita un `ldconfig` x86 bajo FEX en cada arranque (no medible aquí: necesita FEX) |
| Comprobar que el Proton ARMv8.0 ya está instalado | 41 ms (arranque de Python) | 5 ms (shell) | Bajo proot el arranque de Python cuesta bastante más que aquí |

Reproducible con los scripts de `evidencia/bench-*.txt`.

## No medible aquí (pendiente en tu teléfono)

| Cambio | Qué debería notarse | Por qué no lo mido aquí |
|---|---|---|
| `-noverifyfiles` para una versión del cliente que ya funcionó | Menos tiempo en "Verifying installation" del cliente x86-64 bajo FEX | Necesita el cliente Steam x86-64 real bajo FEX |
| Vigilancia del primer fotograma | Si la GPU del menú falla: se pasa a software en vez de esperar indefinidamente | Necesita tu combinación Adreno 610 + Turnip + thunks de FEX |
| Proton ARM64 reescrito (v2) | Menos CPU para Wine/DXVK al arrancar y jugar | Necesita juegos reales |

## Cómo comparar en tu teléfono (ya instrumentado)

La v3 calcula los tiempos **a partir de los registros que la sesión ya escribía también en la v1/v2**
(`events.jsonl` y las líneas `== STEP` de `session.log`), así que puedo calcular los mismos tiempos de un
ZIP de registros de la v2 y de la v3:

1. Abre DroidDeck desde cerrado (cuenta como **apertura de la app**).
2. Pulsa Play en Steam y espera a ver Steam (**Linux**, **FEX + cliente x86-64**, **Steam**, **total**).
3. Abre un juego (**lanzamiento → primera imagen** y **→ fluido**: 3 s seguidos a ≥ 20 fps; una pantalla de
   carga animada también cuenta, así que no es exactamente "jugable").
4. Repite 3 veces. El primer inicio (descargas, instalaciones) se guarda aparte de los siguientes.
5. **Compartir registros** → el ZIP lleva `timings.txt` con la mediana de los 5 últimos y el último valor de
   cada fase.

Lo que no desaparece por mucho que se optimice: el tiempo de carga propio de cada juego, el de Steam
descargando actualizaciones y la compilación de shaders necesaria la primera vez (la caché de disco de Mesa
y la de FEX se conservan entre arranques, así que la segunda vez cuesta menos).
