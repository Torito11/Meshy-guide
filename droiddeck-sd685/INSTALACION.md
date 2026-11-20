# Instalación, primer uso y actualización

## Importante antes de instalar: por qué es una app aparte

La APK oficial 0.7.1 está firmada con la **clave privada del proyecto DroidDeck** (certificado
`CN=DroidDeck, O=The412Banner`, SHA-256 `b241ea7d…5d3f0`), con una rotación de firma que rechaza
expresamente cualquier APK firmada con otra clave. Nadie salvo el proyecto puede firmar una actualización
para `com.droiddeck.launcher`.

Por eso esta versión se instala como **otra app**: `com.droiddeck.launcher.sd685`, con el nombre
**"DroidDeck SD685"**.

- **No toca tu DroidDeck oficial ni sus datos.** Ambas pueden convivir.
- A cambio, la nueva app empieza de cero: hay que instalar su runtime Linux, iniciar sesión en Steam y
  descargar los juegos de nuevo dentro de ella. Necesitas unos 6–8 GB libres (tienes ~150 GB).
- Usar el mismo identificador obligaría a **desinstalar la oficial, lo que borra sus datos**. No lo hice
  porque pediste no borrar nada.

## Instalar

1. Copia `DroidDeck-0.7.1-sd685.apk` al teléfono y ábrelo. Permite "instalar apps desconocidas" al
   gestor de archivos o navegador que uses.
2. Comprueba la huella antes de instalar si quieres (está en `apk/SHA256SUMS`).
3. Android 15 avisará de que la app está hecha para una versión antigua de Android (`targetSdk 28`, igual
   que la oficial). Pulsa "Instalar de todos modos". Play Protect puede pedir confirmación porque la firma
   es la *testkey* pública de AOSP (la misma con la que se compilan las builds locales del proyecto).
4. Abre **DroidDeck SD685** e instala el runtime Linux cuando lo pida (~3 GB de descarga).
5. En Opciones de desarrollador ya tienes desactivadas las restricciones de procesos hijos (tu informe dice
   "Phantom proc monitor disabled"); no hace falta repetirlo.

Desinstalar "DroidDeck SD685" borra solo los datos de esa app.

## Primer arranque de Steam

1. Pulsa **Play**. La app detecta que tu CPU es ARMv8.0 y usa el **cliente Steam x86-64 bajo FEX**
   automáticamente (en Ajustes de Steam → Cliente de Steam solo aparece x86-64, con la explicación).
2. La primera vez descarga: FEX, el rootfs x86 de Ubuntu 24.04 (~500 MB), el cliente Steam x86-64 y
   las piezas del cliente ARM64 que DroidDeck usa como base. Puede tardar 5–15 min según tu conexión.
   Mantén el teléfono enchufado o con batería suficiente y la pantalla encendida.
3. Inicia sesión en Steam. La interfaz irá **lenta** (todo el cliente se traduce de x86): es normal en
   esta CPU.
4. Para juegos de Windows, DroidDeck SD685 pide a Steam que instale **Proton Experimental** y lo ejecuta con
   la herramienta "DroidDeck Proton x86-64 (FEX, no container)", que queda como predeterminada.
   Si un juego dice que no hay Proton, instala "Proton Experimental" desde Biblioteca → Herramientas.

## Ajustes recomendados para el Snapdragon 685

| Ajuste | Valor | Motivo |
|---|---|---|
| Pantalla → Frecuencia de la sesión | **60 Hz** (ya viene así en gama baja) | Mitad de trabajo de composición y menos calor que 120 Hz. |
| Pantalla → Resolución | 720p (1600×720) para la interfaz; dentro de los juegos, 1280×720 o menos | La Adreno 610 no da para más. |
| Rendimiento → Preset de FEX | `PERFORMANCE_TSO` (el tuyo) | Equilibrio estabilidad/velocidad. `PERFORMANCE` (sin TSO) es más rápido pero puede colgar juegos multihilo; pruébalo solo por juego. |
| Rendimiento → Turnip sysmem | Activado (por defecto) | La A610 tiene poca memoria GMEM; el renderizado en memoria del sistema evita *tiling* costoso. |
| Rendimiento → zRAM | Activado (por defecto) | Comprime Steam mientras juegas y deja RAM al juego. |
| Rendimiento → Núcleos del juego (opcional) | 4,5,6,7 | Los A73 son ~2–3× más rápidos que los A53. Pruébalo por juego: limita a 4 hilos. |
| HUD de rendimiento | Desactivado salvo para medir | Consume CPU/GPU. |

Fuera de DroidDeck (sin root, sin tocar el sistema):

- Juega con el teléfono **frío** y sin cargar: tu registro muestra estado térmico SEVERE y los núcleos
  grandes limitados a 2,4 GHz *antes* de abrir Steam. Quitar la funda y evitar cargar mientras juegas
  ayuda más que cualquier ajuste.
- HyperOS → Batería → modo **Rendimiento** mientras juegas (y "Game Turbo" si lo usas: añade DroidDeck SD685).
- Cierra apps en segundo plano: con ~3,5 GB libres, cada GB cuenta.

## Actualizar

- Esta app **no se actualiza sola** desde las releases oficiales (es una compilación local; la app lo indica
  con la marca "LOCAL" en una esquina).
- Cuando salga una versión oficial nueva, mira si incluye el cambio automático de cliente para CPUs
  ARMv8.0 (busca "ARMv8.0" o "LSE" en sus notas). Si lo incluye, puedes volver a la app oficial.
- Para recompilar esta versión: `build/rebuild.sh` (descarga el código oficial 0.7.1, aplica los parches de
  `patches/`, prepara las entradas nativas y compila). Para una versión oficial más nueva, los parches
  pueden necesitar adaptación (`git am -3`).
- Una nueva compilación con el mismo identificador `.sd685` y la misma *testkey* se instala **encima** de
  esta conservando sus datos.

## Volver atrás

Tu DroidDeck oficial sigue intacto. Si algo no te convence, desinstala "DroidDeck SD685" y sigue usando la
oficial (con el cliente x86-64 elegido a mano en Ajustes de Steam → Cliente de Steam, que es lo más
parecido sin esta versión).
