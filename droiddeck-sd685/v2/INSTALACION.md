# Instalación y actualización — DroidDeck 0.7.1-sd685.2 (v2)

## Resumen

| Tienes instalado… | Qué pasa al instalar la v2 |
|---|---|
| **DroidDeck SD685 (v1)** | Se **actualiza** encima: mismo paquete (`com.droiddeck.launcher.sd685`) y misma firma. **Conserva tus datos**: runtime Linux, sesión de Steam, juegos descargados, cuentas de tiendas y ajustes. |
| Solo el **DroidDeck oficial** | Se instala **como app aparte** ("DroidDeck SD685"). La oficial y sus datos **no se tocan**. |
| Nada | Instalación nueva. |

**Firma:** la APK está firmada con la *testkey* pública de AOSP, igual que la v1. La APK oficial está
firmada con la clave privada del proyecto DroidDeck (`CN=DroidDeck, O=The412Banner`), con una rotación
de firma que rechaza cualquier otra clave: **nadie salvo el proyecto puede publicar una actualización de
`com.droiddeck.launcher`**. Por eso esta versión no puede actualizar la oficial y usa su propio paquete.
Para pasar tus juegos de la oficial a esta, hay que descargarlos de nuevo dentro de "DroidDeck SD685"
(o añadir la carpeta de biblioteca de Steam si la tienes en almacenamiento compartido).

## Instalar / actualizar

1. Copia `apk/DroidDeck-0.7.1-sd685.2.apk` al teléfono. Comprueba la huella si quieres
   (`apk/SHA256SUMS`).
2. Ábrela. Si ya tenías la v1, Android mostrará **"¿Quieres actualizar esta app?"** → *Actualizar*.
3. Android 15 avisa de que la app está hecha para una versión antigua (`targetSdk 28`, igual que la
   oficial) y Play Protect puede pedir confirmación por la *testkey*: *Instalar de todos modos*.
4. Comprueba en *Ajustes de Android → Aplicaciones → DroidDeck SD685* que la versión es **0.7.1-sd685.2**.

## Primera sesión de Steam con la v2

1. Pulsa **Play**. Verás un paso nuevo: *"checking Proton for this CPU (ARMv8.0…)"*.
   - Si ya tenías **DroidDeck-Proton 11-12.8** instalado, se usa como base: no descarga nada y tarda
     unos minutos (copia y parcheado de 688 archivos).
   - Si no, descarga la release oficial (~626 MB, una sola vez, con reanudación) y la verifica por
     SHA-256 antes de parchearla. Necesita ~3 GB libres durante la instalación.
   - Si falla (sin conexión, poco espacio), la sesión **sigue** con el Proton x86-64 de la v1 y lo
     reintenta en la próxima sesión.
2. Los juegos de Windows usarán **"DroidDeck-Proton 11-12.8 (ARMv8.0)"** automáticamente.
   Para un juego concreto: *Steam → juego → Propiedades → Compatibilidad*. Ahí siguen también
   `droiddeck-proton-x64` (el de la v1) como alternativa si un juego no funciona con el ARM64.

## Elegir un perfil

*Ajustes del modo Steam (los ajustes de la sesión) → pestaña **Pantalla** → grupo **Perfil de rendimiento***:
**Equilibrado** (por defecto de DroidDeck), **Rendimiento**, **Ahorro**, **Compatibilidad**,
**Xbox (PC)**, **Xbox Cloud**, **Steam**. La explicación de cada uno aparece debajo del selector y en
`OPTIMIZACION.md` §2. Los cambios de sesión (30/60 Hz, núcleos, FEX) se aplican en la **próxima
sesión**; los de Xbox Cloud, en el **próximo stream**. Si cambias un ajuste a mano, el perfil aparece
como *Personalizado*; elige uno de nuevo para volver a sus valores.

Sugerencia de partida para tu Redmi Note 13: **Steam** para juegos de Steam, **Xbox Cloud** para la nube,
**Ahorro** si el teléfono se calienta o quieres más batería.

## Volver a la v1 (copia de seguridad)

La v1 sigue en `../apk/DroidDeck-0.7.1-sd685.apk` (sin modificar). Tiene el mismo `versionCode` (19), así
que Android permite instalarla encima de la v2 **conservando los datos**. La herramienta
"DroidDeck-Proton 11-12.8 (ARMv8.0)" seguiría instalada (carpeta
`compatibilitytools.d/ARMv8.0-DroidDeck-Proton-11-12.8` de Steam) y podrías seguir eligiéndola por juego,
pero la v1 no la pone por defecto.

## Desinstalar

Desinstalar "DroidDeck SD685" borra solo los datos de esa app. La oficial no se ve afectada.
