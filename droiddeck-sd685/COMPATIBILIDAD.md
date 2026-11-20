# Qué puede funcionar en el Redmi Note 13 (Snapdragon 685 / Adreno 610)

Esto es una estimación técnica razonada, **no** una lista probada en tu teléfono: no tuve acceso al
dispositivo. Distingue siempre entre ejecutar un juego **en el teléfono** (local) y **transmitirlo** desde
servidores de Microsoft (nube).

## Cómo se ejecuta cada cosa en tu CPU con esta versión

| Tipo de juego | Ruta en DroidDeck SD685 | ¿Viable en ARMv8.0? |
|---|---|---|
| Cliente Steam | Cliente x86-64 de Valve bajo FEX (automático) | Sí, lento |
| Juego de Windows (Steam) | `droiddeck-proton-x64`: Proton x86-64 de Valve bajo FEX, sin contenedor | Experimental (nuevo, sin probar en dispositivo) |
| Juego Linux x86 (Steam) | `droiddeck-direct` bajo FEX (ruta ya existente del proyecto) | Sí, es la ruta que el proyecto ya usa |
| Juego Linux ARM64 nativo | Directo | Sí |
| Proton ARM64 (Valve, GE, DroidDeck-Proton) | — | **No**: compilado para ARMv8.2 → SIGILL |
| Juegos de PC de Xbox/Game Pass instalados en local (tienda Xbox de DroidDeck) | Proton ARM64 | **No** en esta CPU (mismo motivo) |
| Epic / GOG / otras tiendas con Proton ARM64 | Proton ARM64 | **No** en esta CPU |
| **Xbox Cloud Gaming** (streaming) | Reproductor web/nativo, vídeo H.264 por hardware | **Sí** |

## Juegos locales: expectativas realistas

Factores que limitan, de más a menos importante:

1. **CPU + traducción FEX**: 4 núcleos A73 (limitados a ~2,4 GHz por temperatura en tu registro). FEX sin
   LSE ni RCPC paga caro cada operación atómica y la emulación del orden de memoria de x86 (TSO). Los
   juegos con mucha lógica en CPU (estrategia grande, mundos abiertos, simulación) serán los peores.
2. **GPU Adreno 610**: apta para 2D y 3D sencillo; DXVK (Direct3D 9/10/11 → Vulkan) añade coste. A
   720p o menos.
3. **RAM**: con el cliente Steam x86-64 abierto quedan unos ~2 GB para el juego. Juegos que piden ≥ 4 GB
   de RAM tienen alto riesgo de cierre.
4. **Antitrampas** de nivel kernel (EasyAntiCheat/BattlEye no habilitados para Proton) y DRM pesado: no.

| Categoría | Expectativa |
|---|---|
| 2D / pixel art / indies ligeros (requisitos tipo "2 GHz, 2 GB RAM, GPU DX9/DX10") | Candidatos con más probabilidad de funcionar. |
| Juegos 3D antiguos (era DX9, ~2004–2010) con requisitos bajos | Posibles a baja resolución. |
| Juegos con versión nativa Linux x86 | Suelen ir mejor que vía Proton (sin capa Wine). |
| 3D modernos (≥ 2015, DX11/DX12, ≥ 4 GB RAM) | No realistas en este hardware. |
| Multijugador competitivo con antitrampas | No. |

Consejo práctico: en la página de Steam de cada juego mira los **requisitos mínimos**; si piden más que un
doble núcleo moderno y una GPU DX10 básica, descártalo en este teléfono.

## Xbox

### Xbox Cloud Gaming (recomendado para juegos de Xbox / Game Pass)

- El juego corre en servidores de Microsoft; el teléfono solo decodifica vídeo y envía los controles. **No
  depende de la CPU ARMv8.0** ni de Proton: es la mejor vía para jugar a títulos de Xbox en este móvil.
- Requiere cuenta Microsoft con **Game Pass Ultimate** (la que incluye la nube) e iniciar sesión en la
  pestaña Xbox de DroidDeck SD685 (es una app distinta: la sesión no se comparte con la oficial).
- Vídeo: el reproductor de DroidDeck negocia H.264 (solo ajusta perfiles H.264, `tools/xcloud-player/sdp-tweaks.ts`),
  que el Snapdragon 685 decodifica por hardware hasta 1080p60. Su falta de decodificador AV1 no afecta.
- Ajustes recomendados (pantalla de ajustes de Xbox Cloud):
  - Resolución **1080p** (tu panel mide 1080 px de alto) con **Wi-Fi de 5 GHz**; si hay cortes, 720p.
  - Códec: "default" o "high". Bitrate automático.
  - Motor del reproductor: **web** (el predeterminado). En esta versión, si eliges el motor *nativo*, la
    generación de fotogramas DDFG viene **desactivada por defecto** en gama baja: su flujo óptico cuesta
    a la Adreno 610 más de lo que aporta y añade latencia. Puedes activarla igualmente.
- Mandos: los mandos Xbox/PlayStation por Bluetooth funcionan a través de la API de mandos de Android;
  también hay controles táctiles.
- Latencia: depende sobre todo de la red (distancia al centro de datos de Microsoft y calidad del Wi-Fi),
  no del teléfono.

### PC Game Pass / tienda Xbox (juegos de PC instalados en el teléfono)

- El inicio de sesión, la biblioteca y las licencias (`xodus-cli`/`xodus-service`) **sí** son
  compatibles con tu CPU (lo comprobé en el binario: usan atomics con comprobación en tiempo de ejecución).
- Ejecutar esos juegos **en local** pasa por Proton ARM64 → **no es posible en ARMv8.0**. Para jugar a esos
  títulos en este teléfono, usa Xbox Cloud Gaming si el juego está en la nube.

## Lo que esta versión no puede cambiar

- La CPU no tiene ni tendrá instrucciones LSE: Valve tendría que publicar binarios ARM64 para ARMv8.0.
- No existe un controlador que haga la Adreno 610 más rápida que su hardware; Turnip (Mesa) ya es el
  controlador abierto adecuado y DroidDeck usa la versión para A6xx.
