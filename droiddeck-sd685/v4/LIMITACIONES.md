# Limitaciones conocidas y recomendaciones — v4

## Lo que no está demostrado

1. **Que el menú de Steam aparezca en tu teléfono con OpenGL por software.** Está demostrado que el rootfs x86
   de tu teléfono crea ese contexto (en x86 nativo y **bajo tu FEX en una CPU ARMv8.0 emulada**) y que el
   cliente Steam real arranca con él sin errores de GL; no pude llegar al menú en el contenedor (sin internet
   directo para Steam y con la conexión interna cliente–ayudante rechazada por el entorno). La v4 lo comprueba
   en tu teléfono antes de usarlo y, si no funciona, para en vez de repetir sin fin.
2. **Velocidad del menú con llvmpipe bajo FEX** en el Snapdragon 685: será lenta (todo el dibujado en la CPU
   y traducido por FEX). No sé cuántos fps tendrás; puede ser incómodo pero usable, o demasiado lento. Los
   juegos no se ven afectados (siguen con la GPU).
3. **Por qué falla del todo el OpenGL de la GPU desde FEX** en tu teléfono. La primera parte la dice el propio
   compositor de DroidDeck en tu `wayland.log` ("this device gives apps no display (DRM) device"): sin nodo DRM
   no hay pantalla DRI3. Lo que no está confirmado es por qué el respaldo (zink por `drisw`) tampoco crea el
   Vulkan de Turnip desde ese camino (`VK_ERROR_INCOMPATIBLE_DRIVER`). La v4 no depende de ello.
4. Tiempo de la primera comprobación de OpenGL: hasta ~1 minuto la primera vez (llvmpipe se inicializa bajo
   FEX); luego queda guardada.
5. Todo lo pendiente de la v3 sigue pendiente en tu teléfono: tiempos reales de arranque, juegos con el
   Proton ARMv8.0, Xbox Cloud con tu cuenta (disponibilidad en Colombia sin confirmar), perfiles, temperatura
   y batería.

## Si la v4 no muestra el menú

- Si ves "**…software OpenGL does not work here either**": `glxinfo` por software tampoco crea un contexto en
  tu teléfono → envíame `x64-gl-probe.txt`; el siguiente paso sería otro camino de GL (p. ej. una pila Mesa
  x86 distinta o un *thunk* GL que use el EGL de Android), no algo que se pueda decidir sin ese archivo.
- Si ves "**Steam restarted its web helper 4 times (OpenGL software…)**": el contexto por software existe pero
  el compositor de Steam aún falla → envíame `steam/webhelper.txt` y `steam/console-linux.txt`.
- Para volver a comprobar el OpenGL: se hace solo cuando cambian FEX, el rootfs o las variables del
  controlador. A mano: borrar `~/.droiddeck-x64/.droiddeck-gl-mode`, o *Reparar Steam* en el menú (ojo: eso
  además vuelve a descargar el cliente, unos 700 MB).

## Recomendaciones (mejoras futuras, no hechas aquí)

1. **GL por GPU para los programas x86 sin DRI3**: investigar por qué el Mesa del lado ARM no obtiene el
   dispositivo (DRM sobre KGSL en proot) o usar un *thunk* GL hacia el EGL/GLES de Android. Daría menús
   rápidos; requiere pruebas en el teléfono.
2. **Modo escritorio de Steam** (`-steamos3` sin `-gamepadui`) como alternativa más ligera para llvmpipe, si el
   modo Big Picture resulta demasiado lento.
3. **Desactivar las actualizaciones automáticas de componentes** del DroidDeck-Proton que se usa como base, o
   guardar el original, para no tener que descargar 626 MB.
4. Probar en el teléfono el resto de la v3 y medir con `timings.txt`.
