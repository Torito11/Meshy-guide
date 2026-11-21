# Instalación y actualización — DroidDeck 0.7.1-sd685.3 (v3)

## Actualizar (sin perder datos)

| Tienes instalado… | Qué pasa |
|---|---|
| **DroidDeck SD685** v1 o v2 | Se **actualiza** encima: mismo paquete `com.droiddeck.launcher.sd685`, misma firma, mismo `versionCode`. Se conservan runtime Linux, sesión de Steam, juegos, cuentas y ajustes. |
| Solo el **DroidDeck oficial** | Se instala aparte ("DroidDeck SD685"); la oficial no se toca (está firmada con la clave privada del proyecto, que nadie más puede usar). |

1. Copia `apk/DroidDeck-0.7.1-sd685.3.apk` al teléfono (huella en `apk/SHA256SUMS`) y ábrela → *Actualizar*.
2. Android 15 / Play Protect pueden avisar (`targetSdk 28` como la oficial, firma *testkey*): *Instalar de todos modos*.
3. Comprueba en *Ajustes de Android → Aplicaciones → DroidDeck SD685* que la versión es **0.7.1-sd685.3**.

## Qué verás de nuevo

- **Al iniciar Steam**: si tarda, la pantalla de carga dice qué hace ("Steam sigue arrancando · 2:05 · CPU del
  cliente 87 % · 2310 MB libres…"). Si el menú de Steam falla con la GPU, verás "Los menús de Steam fallaron
  con la GPU…: reiniciando Steam con renderizado por software" y Steam arrancará de nuevo solo, una vez.
- **Tras 90 s esperando**: botón **Compartir registros** abajo a la izquierda, sin tener que cancelar.
- **Primer arranque tras actualizar**: los enlaces del runtime de Steam se rehacen una vez; los siguientes
  arranques se lo saltan. Si ya tenías el Proton ARMv8.0, no se descarga nada.
- **Xbox Cloud** (*Tiendas → Xbox → Ajustes de nube*): región **"Menor latencia medida"**, interruptor
  **Calidad automática** y sección **Estadísticas** (última transmisión, latencia por región con botón
  *Medir la latencia ahora*, y si tu decodificador admite 1080p60).
- **Perfiles** (*Ajustes del modo → Pantalla → Perfil de rendimiento*): ahora "Máximo rendimiento seguro";
  Rendimiento y Xbox Cloud eligen la región de menor latencia.

## Enviarme registros (si algo falla)

*Compartir registros* (en la pantalla de carga tras 90 s, en el menú lateral de la sesión o al terminar una
sesión). El ZIP censura datos personales e incluye `session.log`, registros de Steam (también del cliente
x86-64), `timings.txt` (tiempos de cada fase, aunque Steam no llegara a mostrarse), `memory.txt` (memoria y
temperatura), `device.txt` (CPU/GPU), el informe gráfico y el de Wayland.

## Volver atrás

Las APK v2 (`../v2/apk/`) y v1 (`../apk/`) siguen disponibles sin modificar; tienen el mismo `versionCode`,
así que se pueden instalar encima conservando datos. Lo que la v3 deja en disco y las versiones anteriores
ignoran: `~/.droiddeck-x64/.droiddeck-cef-software`, `.droiddeck-client-ok`, `steamrt-libs/.droiddeck-stamp`
y `files/startup-times.jsonl`.
