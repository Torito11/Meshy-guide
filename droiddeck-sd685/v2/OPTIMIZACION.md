# Informe de optimización — DroidDeck 0.7.1-sd685.2 (v2)

Dispositivo objetivo: **Redmi Note 13 (23129RA5FL, "sapphire")** · Snapdragon 685 (SM6225: 4× Cortex-A73
a 2,8 GHz + 4× Cortex-A53 a 1,9 GHz, **ARMv8.0**) · Adreno 610 · 8 GB · Android 15 / HyperOS 2.0.

Esta versión parte de la v1 (`0.7.1-sd685`) y **conserva todas sus reparaciones**. No se ha empezado de cero.

## Cómo leer los resultados

| Marca | Significado |
|---|---|
| ✅ **Ejecutado** | Ejecutado aquí: compilación, tests unitarios Kotlin/Python, análisis de binarios. |
| 🧪 **Emulado** | Probado en una **CPU ARMv8.0 emulada** (QEMU `cortex-a53`, sin LSE: el mismo juego de instrucciones que tu SD685) con un **kernel Linux real** (Ubuntu 24.04 arm64, 6.8) en máquina virtual. Demuestra que el código **funciona y da resultados correctos**; **no** mide rendimiento (la emulación es decenas de veces más lenta). |
| ⏳ **Pendiente** | Necesita tu Redmi Note 13. No tengo acceso al teléfono. |
| 📐 **Estimación** | Razonamiento técnico, no una medida. |

**No hay cifras de FPS en este informe**: no he podido medirlas en tu teléfono y no las invento. Al final
tienes cómo medirlas tú (§10).

---

## 1. El cambio más importante: Proton ARM64 funcionando en tu CPU (P3)

**Problema (confirmado en v1):** todas las builds ARM64 de Proton (DroidDeck-Proton, Proton-GE arm64…)
se compilan para ARMv8.2 y usan **instrucciones atómicas LSE** (ARMv8.1: `CAS`, `LDADD`, `SWP`…) sin
comprobar si la CPU las tiene. Los Cortex-A53/A73 no las tienen → `SIGILL` (error 132) al arrancar.

**v1 (solución de compromiso):** los juegos de Windows usaban el **Proton x86-64 de Valve entero bajo
FEX**. Funciona, pero FEX tiene que traducir *todo*: el juego, Wine (ntdll, kernel32, win32u…), DXVK /
vkd3d-proton (la traducción Direct3D→Vulkan, muy intensiva en CPU) y el cargador de Vulkan.

**v2 (solución real):** reescritura binaria de Proton ARM64 para ARMv8.0 (`tools/armv80/`, código nuevo):

- Cada instrucción LSE se sustituye por un salto a una secuencia equivalente de ARMv8.0
  (`LDXR`/`LDAXR` + operación + `STXR`/`STLXR` en bucle), con **la misma semántica de memoria**
  (acquire/release), preservando registros y flags, en un segmento ejecutable nuevo. `LDAPR` → `LDAR`.
  `CASP` de 128 bits incluido. En PE ARM64EC solo se tocan rangos ARM64/ARM64EC del *code map* (no x64).
- **688 archivos, 53.158 instrucciones reescritas, 0 restantes** ✅ (`evidencia/lse-census.txt`).
- En el teléfono se instala como **parche de 787 KB** incluido en la APK sobre la release oficial de
  DroidDeck-Proton 11-12.8, verificada por SHA-256; **cada archivo se comprueba antes y después** de
  parchear. Si ya tienes DroidDeck-Proton 11-12.8 instalado, se usa como base **sin descargar nada** y
  sin modificarlo (se crea una herramienta aparte: *"DroidDeck-Proton 11-12.8 (ARMv8.0)"*).
- El cliente Steam x86-64 la usa por defecto en tu CPU; `droiddeck-proton-x64` (v1) queda de respaldo.

**Por qué rinde más** 📐: con Proton ARM64, Wine, DXVK y vkd3d son **código ARM64 nativo**; FEX solo
traduce el código x86 **del propio juego** (ARM64EC para x64, WoW64 para x86 de 32 bits). La parte
gráfica deja de pagar la traducción. Cuánto se nota depende del juego (más en juegos limitados por CPU o
por muchas llamadas de dibujo). **Medición real ⏳.**

**Pruebas** (detalle en `PRUEBAS.md`):

| Prueba | Resultado |
|---|---|
| Test de atómicas (63 formas LSE, CAS 128 bits, 4 hilos en contención), CPU sin LSE | 🧪 Original: `SIGILL`. Reescrito: resultados **idénticos** a la CPU con LSE, 800000/800000 |
| `wine` de DroidDeck-Proton en Cortex-A53, kernel real | 🧪 Original: error 132. Reescrito: arranca |
| Programa Windows **x86-64** (atómicas, 4 hilos, FP, heap) vía FEX ARM64EC | 🧪 **OK** (con y sin fsync) |
| Programa Windows **x86 de 32 bits** vía FEX WoW64 | 🧪 **OK** (con y sin fsync) |
| Script `proton run` completo (como lo lanza Steam), pantalla virtual 1600×720 | 🧪 **OK** x86 y x86-64 |
| Juego real en el Redmi Note 13 | ⏳ |

**Limitaciones honestas:**
- Solo **DroidDeck-Proton 11-12.8** (la versión fijada en el parche). Otras builds arm64 siguen sin
  usarse en tu CPU. Una versión futura necesita regenerar el parche con `tools/armv80/rewrite_tree.py`.
- El **cliente Steam ARM64 de Valve no se parchea**: es binario cerrado, se autoactualiza y verifica sus
  archivos; sigue el cliente x86-64 bajo FEX de la v1 (lento en la interfaz, pero funcional).
- Primer uso: ~626 MB de descarga (si no tienes ya 11-12.8) y ~3 GB libres temporalmente.

## 2. Perfiles de rendimiento (P0)

Nuevo selector **Ajustes del modo → Pantalla → Perfil de rendimiento**. Cada perfil **solo escribe
ajustes que DroidDeck ya tenía**, todos reversibles; si luego cambias uno a mano, el perfil aparece como
**Personalizado**. Ninguno toca frecuencias de CPU/GPU, límites térmicos ni ajustes de Android.

Valores para tu dispositivo (GPU de gama baja, núcleos de eficiencia `0,1,2,3`):

| Perfil | Sesión | FEX | Cliente Steam | Pistas hilos | Shaders 2.º plano | Xbox Cloud |
|---|---|---|---|---|---|---|
| **Equilibrado** | 60 Hz | PERFORMANCE_TSO | todos los núcleos | no | (sin cambio) | 1080p, sin gen. fotogramas, búfer normal |
| **Rendimiento** | 60 Hz | PERFORMANCE_TSO | núcleos A53 (gamescope libre) | sí | no | menor latencia: búfer pequeño, decodificador rápido, copia cero |
| **Ahorro** | **30 Hz** | PERFORMANCE_TSO | A53 (y gamescope) | no | no (+ sin descargas en 2.º plano) | 720p, 8 Mb/s, pantalla a 60 Hz |
| **Compatibilidad** | 60 Hz | **COMPATIBILITY** (TSO completo, x87 exacto) | todos | no | (sin cambio) | motor web, búfer normal, sin copia cero |
| **Xbox (PC)** | 30 Hz | PERFORMANCE_TSO | A53 (gamescope libre) | sí | no | (sin cambio) |
| **Xbox Cloud** | (sin cambio) | (sin cambio) | (sin cambio) | (sin cambio) | (sin cambio) | 1080p, búfer pequeño, decodificador rápido, copia cero |
| **Steam** | 60 Hz | PERFORMANCE_TSO | A53 (gamescope libre) | sí | no | (sin cambio) |

**Justificación de cada parámetro:**
- **30 Hz**: gamescope recibe `-r 30` → la mitad de fotogramas → 📐 aproximadamente la mitad de trabajo
  de GPU en juegos limitados por GPU, menos calor y batería. 30 divide exactamente 60 → ritmo regular,
  sin tirones de cadencia. (Opción nueva también en *Frecuencia de la sesión*.)
- **Cliente Steam en los A53**: en tu CPU el cliente y su `steamwebhelper` (Chromium) son x86-64
  traducidos por FEX y compiten con el juego por los 4 núcleos A73. Fijarlos en los A53 deja los A73
  para el juego. Los juegos lanzados **no heredan** esa restricción: DroidDeck ya reasigna su afinidad a
  todos los núcleos (`CpuCores.gameLaunchList`). En Rendimiento/Steam/Xbox **gamescope no se fija** (es el
  compositor del juego: mejor en cualquier núcleo); en Ahorro sí.
- **Pistas de hilos (ADPF)**: API oficial de Android (`PerformanceHintManager`) que indica al sistema que
  los 2 hilos más ocupados del juego van retrasados; **Android decide** las frecuencias, nada se fuerza.
  Antes solo se activaba en el AYN Odin 3; ahora también en otros SoC al elegir un perfil, y **se detiene
  con estado térmico SEVERE** (en el Odin 3 con CRITICAL), en modo ahorro de batería, y cuando el juego
  mantiene su ritmo 10 s. En el registro que me enviaste el teléfono llegó a **SEVERE**: ahí las pistas se apagan solas.
- **Sin precompilación de shaders en segundo plano**: el `fossilize_replay` de Steam usa todos los núcleos
  durante minutos (bajo FEX, más) y calienta el teléfono; DroidDeck ya lo desactivaba en instalaciones
  nuevas, el perfil lo garantiza.
- **FEX COMPATIBILITY**: orden de memoria x86 en todas las operaciones (también vectoriales y memcpy) y
  x87 de 80 bits: más lento, para juegos que fallan o muestran errores con el preset rápido.

**Detección de modalidad / recursos no usados** (ya existía, verificado en código): al dejar la sesión
Steam en segundo plano (p. ej. para jugar en Xbox Cloud), la política de suspensión por defecto de Steam
(`native`) **suspende la sesión Linux** en cuanto Steam está listo para dormir, salvo que haya descargas
activas, así que no compite por la CPU mientras haces streaming. El perfil Xbox Cloud no toca nada de la
sesión local.

## 3. CPU

- ✅ Implementado: perfiles, fijación del cliente a los A53, pistas ADPF con corte térmico.
- Mantenido: preset FEX **PERFORMANCE_TSO** por defecto (TSO en accesos principales, x87 de precisión
  reducida, multiblock). No elijo `PERFORMANCE`/`EXTREME` (sin TSO) por defecto: rompen juegos
  multihilo y la regla es no sacrificar estabilidad.
- No hecho (y por qué): fijar *governors* o frecuencias (requiere root y lo prohíbes); parchear el
  cliente Steam ARM64 (cerrado y autoactualizable).

## 4. GPU, FPS, temperatura y batería

- v1: sesión limitada a **60 Hz** en GPU de gama baja (tu panel es de 120 Hz), generación de fotogramas
  DDFG desactivada en xCloud (en Adreno 610 cuesta más de lo que aporta).
- v2: opción y perfiles a **30 Hz**; menos trabajo en segundo plano (shaders/descargas) en Ahorro.
- No se desactiva ninguna protección térmica ni se fuerzan frecuencias.
- ⏳ Medir: temperatura y estado térmico (informe de dispositivo), consumo por cada 30 min.

## 5. RAM (8 GB, ~3,5 GB libres en tu log)

- 📐 Con Proton ARM64, FEX ya no mantiene caché de código traducido para Wine/DXVK (solo para el juego).
- 📐 Sin `fossilize_replay` en segundo plano se evitan procesos que pueden ocupar cientos de MB.
- Sin cambios en zram/límites de RAM existentes (`ramCapMb`, `zramClient`): siguen siendo tuyos.

## 6. Xbox "normal" (P1) — auditoría de lo que DroidDeck tiene de verdad

Verificado en el código fuente (no se ha inventado nada):

| Función | Estado en DroidDeck | Cambio en v2 |
|---|---|---|
| Inicio de sesión Microsoft | Páginas oficiales (`login.live.com`, `login.microsoftonline.com`, `sisu.xboxlive.com`…) en un WebView limitado a esos dominios | Ninguno (se conserva el inicio oficial) |
| Biblioteca y Game Pass | Juegos propios + catálogos PC Game Pass, Game Pass Ultimate, Premium y Essential | Ninguno |
| Instalar / actualizar juegos de PC y contenido (DLC) | Sí (`XboxInstaller`, `XboxContent`) | Ninguno |
| Lanzar y gestionar juegos de PC | Sí, localmente con Proton como acceso directo de Steam, con concesiones de licencia (`XboxRuntime`, `XboxLaunchLeases`) | **En tu CPU ahora usan el Proton ARM64 reescrito** en lugar del x86-64 bajo FEX |
| Guardado en la nube | Sí (`CloudSaves`) | Ninguno |
| Mandos | Sí (también en la nube: `XboxNativePad`) | Ninguno |
| Juego remoto desde una consola Xbox (xHome) | **No existe en el código** | No se inventa |
| Logros | **No existe en el código** | No se inventa |

Límite honesto: los juegos de Xbox para PC (GDK, normalmente DirectX 12) son exigentes; en una Adreno
610 muchos no serán jugables. El perfil **Xbox (PC)** apunta a 30 fps estables. ⏳

## 7. Xbox Cloud Gaming (P2)

Lo que hay (auditado): **motor web** (WebView + reproductor propio de DroidDeck sobre el WebRTC de
Chromium, decodificación por hardware MediaCodec; es el predeterminado), **motor nativo** experimental
(WebRTC de Google + decodificador MediaCodec de baja latencia; con generación de fotogramas o, sin ella,
**copia cero**: el decodificador pinta directamente en la pantalla sin pasar por la GPU) y, como
alternativa, el **reproductor oficial de Microsoft**. La nube **no ejecuta nada en tu teléfono**: solo
decodifica vídeo.

Cambios v2:
- ✅ El reproductor **web** ahora respeta el límite de fps para la **frecuencia de pantalla** (antes
  ignoraba el límite y la pantalla podía quedarse a 120 Hz con un stream de 60 fps). Con límite 60 →
  modo de 60 Hz. Sin límite se mantiene la elección del sistema.
- ✅ Perfiles Xbox Cloud / Rendimiento / Ahorro / Compatibilidad con valores coherentes (tabla §2).
- Hallazgo analizado y **mantenido**: el motor nativo sin límite elige la frecuencia máxima (120 Hz).
  Con un stream de 60 fps no añade fluidez, pero reduce la espera media hasta el siguiente refresco
  (📐 ~4 ms menos de latencia media). Es un compromiso latencia/batería: el perfil **Ahorro** fija 60 Hz.
- Se conserva: inicio de sesión oficial, cierre ordenado de la sesión tras 45 s en segundo plano en el
  motor nativo (antes de que Android pause la app), reinicio del stream, mandos y vibración.
- Recomendación para tu teléfono: perfil **Xbox Cloud** con resolución 1080p. Si hay tirones: perfil
  **Ahorro** (720p, 8 Mb/s) o **Compatibilidad** (motor web y búfer normal, más tolerante a la red).

## 8. Auditoría profunda — hallazgos y decisiones

| # | Hallazgo | Decisión |
|---|---|---|
| 1 | Todas las builds Proton ARM64 hacen `SIGILL` en ARMv8.0 | **Corregido** (reescritura LSE, §1) |
| 2 | La app instalaba automáticamente Protons ARM64 inutilizables en tu CPU | **Corregido**: no se autoinstalan en ARMv8.0 |
| 3 | El reproductor web de xCloud ignoraba el límite de fps para la pantalla | **Corregido** (§7) |
| 4 | Pistas ADPF limitadas a un único dispositivo (Odin 3) | **Ampliado** con corte térmico más temprano (§2) |
| 5 | Fijar el cliente a núcleos también fijaba gamescope | **Opcional** ahora (los perfiles de rendimiento lo dejan libre) |
| 6 | Sin opción por debajo de 60 Hz para ahorrar | **Añadido** 30 Hz |
| 7 | El motor nativo xCloud usa 120 Hz sin límite | Analizado, **mantenido** (latencia) con alternativa en Ahorro |
| 8 | Prueba de Proton colgada en la VM | Causa: **sin pantalla** en la VM (entorno). Con pantalla virtual pasa |
| 9 | 4 tests Python fallan en este contenedor | **Preexistentes** (sin IPv6, cabeceras); fallan igual en el código original |

No cambiado a propósito: el cliente Steam ARM64 (cerrado), frecuencias/governors (root), un control
térmico automático que baje los fps en caliente (necesita datos reales del teléfono para no empeorar la
experiencia; los perfiles dan ese control de forma manual y predecible).

## 9. Comparativa antes / después

| Aspecto | Original 0.7.1 | v1 (0.7.1-sd685) | v2 (0.7.1-sd685.2) |
|---|---|---|---|
| Steam en tu CPU | `SIGILL` (132) | Cliente x86-64 bajo FEX ✅ | Igual que v1 |
| Juegos Windows (Steam, tiendas, Xbox PC) | No arrancan | Proton x86-64 de Valve **entero** bajo FEX | **Proton ARM64 nativo** (reescrito); FEX solo para el juego 🧪 |
| DroidDeck-Proton / Protons ARM64 | `SIGILL` | `SIGILL` (no se usaban) | DroidDeck-Proton 11-12.8 (ARMv8.0) funciona 🧪 |
| Perfiles | — | — | 7 perfiles |
| Frecuencia de la sesión | Máximo del panel (120 Hz) | 60 Hz por defecto | 60 Hz por defecto, opción 30 Hz |
| Cliente Steam vs juego (núcleos) | Compiten | Compiten | El cliente puede ir a los A53 (perfiles) |
| Pistas de rendimiento de hilos | Solo Odin 3 | Solo Odin 3 | También tu SoC con perfil, se apagan en SEVERE |
| xCloud (motor nativo): generación de fotogramas en Adreno 610 | DDFG por defecto | Desactivada | Desactivada |
| xCloud web: frecuencia de pantalla | La del sistema | La del sistema | Sigue el límite de fps |
| FPS reales en tu teléfono | — | ⏳ | ⏳ |

## 10. Cómo medir en tu Redmi Note 13 (⏳)

1. Mismo juego, misma escena, 10 minutos por prueba, batería > 50 %, sin cargador.
2. FPS: superposición de rendimiento de Steam (botón `…` → Rendimiento → nivel 1–2) o el HUD de DroidDeck.
3. Temperatura/estado térmico: **Compartir registros** → `device.txt` ("Thermal status").
4. Compara: **Proton x86-64 (v1)** frente a **DroidDeck-Proton 11-12.8 (ARMv8.0)** en Propiedades →
   Compatibilidad del juego; y los perfiles **Equilibrado / Rendimiento / Ahorro**.
5. Si un juego falla con el Proton ARMv8.0, vuelve a `droiddeck-proton-x64` para ese juego y envíame
   los registros (Compartir registros).
