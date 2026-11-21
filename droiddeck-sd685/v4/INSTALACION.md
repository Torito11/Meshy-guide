# Instalación y prueba en tu teléfono — DroidDeck 0.7.1-sd685.4 (v4)

## Actualizar (sin perder datos)

| Tienes instalado… | Qué pasa |
|---|---|
| **DroidDeck SD685** v1, v2 o v3 | Se **actualiza** encima: mismo paquete `com.droiddeck.launcher.sd685`, misma firma, mismo `versionCode`. Se conservan runtime Linux, rootfs x86, cliente Steam, sesión, juegos, cuentas y ajustes. |
| Solo el **DroidDeck oficial** | Se instala aparte ("DroidDeck SD685"); la oficial no se toca. |

1. Copia `apk/DroidDeck-0.7.1-sd685.4.apk` al teléfono (huella en `apk/SHA256SUMS`) y ábrela → *Actualizar*.
2. Android 15 / Play Protect pueden avisar (firma *testkey*, `targetSdk 28` como la oficial): *Instalar de todos modos*.
3. Comprueba en *Ajustes de Android → Aplicaciones → DroidDeck SD685* que la versión es **0.7.1-sd685.4**.

No hace falta borrar nada. La v4 no borra juegos, runtime, cuentas ni configuraciones: solo deja de usar la
marca de la v3 que no servía y añade `~/.droiddeck-x64/.droiddeck-gl-mode` (su decisión de OpenGL).

## Qué deberías ver al iniciar Steam (primera vez tras actualizar)

1. "**Comprobando qué OpenGL puede usar el menú de Steam en este dispositivo (solo una vez)**": unos
   segundos (hasta ~1 min la primera vez, porque llvmpipe se prepara bajo FEX). No se repite en los siguientes
   inicios.
2. Según tus registros, lo esperable es que la prueba por GPU falle y la de software funcione. Entonces Steam
   arranca directamente con OpenGL por software.
3. Si aun así el compositor de Steam fallara por GPU, verás "**El menú de Steam no pudo obtener OpenGL en la
   GPU…: reiniciando Steam con OpenGL por software**" y Steam se reinicia solo, **una vez**.
4. Si Steam reiniciara su ayudante web 4 veces, verás "**No se pudo mostrar el menú de Steam: reinició su
   ayudante web 4 veces. Se detuvo Steam en lugar de reintentarlo sin fin. Comparte los registros**": ahí
   necesito tus registros nuevos.
5. Cada 30 s mientras arranca: "Steam sigue arrancando · 1:35 · CPU del cliente 40 % · … · ayudante web
   reiniciado N veces".

Con OpenGL por software el **menú de Steam será lento** (llvmpipe en la CPU, bajo FEX); los **juegos** no
cambian: siguen usando la GPU.

## Proton ARMv8.0

Si tu DroidDeck-Proton 11-12.8 instalado tiene componentes actualizados (como en tus registros), verás
"**the installed DroidDeck-Proton 11-12.8 has d3d12.dll replaced… (626 MB download, once)**" y el progreso
de la descarga. Se descarga una sola vez (se reanuda si se corta) y luego no se repite. Tu DroidDeck-Proton
11-12.8 instalado no se modifica.

## Qué necesito que me envíes

Pruebes lo que pruebes, *Compartir registros* (pantalla de carga tras 90 s, menú lateral de la sesión o al
terminar). En el ZIP de la v4 los registros de Steam ya llevan su nombre real. Lo más importante:

- `x64-gl-probe.txt` — qué OpenGL funcionó en tu teléfono y por qué (con la salida de `glxinfo`).
- `steam-x64/droiddeck-gl-mode.txt` — la decisión guardada.
- `steam/webhelper.txt`, `steam/steamui_html.txt` — si el compositor obtuvo OpenGL y si hubo reinicios.
- `timings.txt` — cuánto tardó cada fase.

Y dime qué viste: ¿apareció el menú de Steam?, ¿cuánto tardó?, ¿se mueve con fluidez suficiente para usarlo?

## Volver atrás

Las APK v3 (`../v3/apk/`), v2 (`../v2/apk/`) y v1 (`../apk/`) siguen sin modificar y tienen el mismo
`versionCode`: se instalan encima conservando datos. La v3 ignora `.droiddeck-gl-mode`.
