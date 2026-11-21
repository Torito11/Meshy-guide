# Limitaciones conocidas y recomendaciones

## Limitaciones (honestas)

1. **No he probado la APK en tu Redmi Note 13.** Está compilada, firmada, verificada y con pruebas
   automáticas; el comportamiento real en el teléfono está pendiente.
2. **Bloqueo de Steam en "Esperando el primer fotograma"**: la causa que encontré en el código (el
   renderizador x86 del menú de Steam que falla con la GPU bajo FEX) es **la más probable, no está
   confirmada** en tu teléfono. Si la causa es otra, la vigilancia lo **muestra en pantalla** (CPU del
   cliente, memoria, actualización, biblioteca que falte) y, tras 90 s, ofrece **Compartir registros**.
   **Necesito ese ZIP** para confirmar o corregir el diagnóstico.
3. **Renderizado por software del menú de Steam** (si la GPU falla): funciona, pero los menús de Steam van
   más lentos. Los juegos no se ven afectados (usan su propio renderizado). Se vuelve a probar la GPU cuando
   el cliente de Steam se actualiza.
4. **`-noverifyfiles`**: si los archivos del cliente se dañaran, Steam no lo detectaría al arrancar; usa
   *Reparar Steam* (que también borra esta marca) o fuerza la verificación con `BL_X64_VERIFY_FILES=1`.
5. **Xbox Cloud Gaming en Colombia**: desde aquí **no he podido confirmar** con una fuente oficial que esté
   disponible (las páginas de xbox.com no son accesibles desde este entorno y la prensa es contradictoria).
   DroidDeck no lo simula: usa exactamente lo que el inicio de sesión de Microsoft devuelve para tu
   cuenta. Si el servicio no se ofrece en tu país, Microsoft no devuelve regiones/transmisión y DroidDeck
   lo indica. **No hay VPN, ni servidores falsos, ni cambios en la autenticación.**
6. **Región por latencia**: solo entre las regiones que Microsoft te ofrece; mide el tiempo de conexión TCP a
   la pasarela de cada región, una aproximación muy cercana (pero no idéntica) a la latencia del vídeo.
7. **Calidad automática**: ajusta el límite de bitrate **para la siguiente transmisión** según lo medido en
   la anterior; dentro de una transmisión ya adaptan WebRTC y los servidores de Microsoft.
8. **Estadísticas**: solo lo que WebRTC informa; lo que no informa aparece como "desconocido".
9. **Tiempo "fluido" de un juego** (≥ 20 fps durante 3 s): una pantalla de carga animada también cuenta;
   no equivale exactamente a "ya se puede jugar".
10. **Proton ARMv8.0**: solo DroidDeck-Proton 11-12.8 (la versión del parche).
11. **Adreno 610**: los juegos DirectX 12 pesados (muchos de Xbox para PC) seguirán sin ser jugables.
12. **Temperatura**: no hay reducción automática de fps al calentarse (las protecciones de Android siguen
    activas); el perfil **Ahorro** (30 Hz) es el control manual.

## Recomendaciones

- **Para el bloqueo de Steam**: instala la v3, abre Steam y, si a los 90 s sigue esperando, pulsa
  **Compartir registros** en la pantalla de carga y envíame el ZIP. Si ves el mensaje "los menús de Steam
  fallaron con la GPU… reiniciando con software", esa era la causa.
- **Steam**: perfil **Steam** o **Máximo rendimiento seguro**; si el teléfono se calienta, **Ahorro**.
- **Xbox Cloud**: perfil **Xbox Cloud** (región por menor latencia, 1080p, calidad automática). Usa Wi-Fi de
  5 GHz cerca del router; mira *Tiendas → Xbox → Ajustes de nube → Estadísticas* tras jugar: si ves pérdida de
  paquetes > 2 %, la siguiente transmisión bajará el bitrate sola.
- **Juegos que fallen con el Proton ARMv8.0**: en Steam → Propiedades → Compatibilidad, elige
  `droiddeck-proton-x64` para ese juego.

## Mejoras futuras posibles

1. Confirmar con tus registros la causa del bloqueo y, si es la GPU, probar el renderizador del menú antes de
   arrancar Steam (sin esperar al fallo).
2. Cambio automático por juego al Proton x86-64 si un juego se cierra al arrancar con el ARM64.
3. Reinicio ICE en xCloud para recuperar cortes de red sin reiniciar la transmisión.
4. Ritmo adaptado a la temperatura (bajar a 30 Hz en estado térmico severo), con datos reales del teléfono.
5. Regenerar el parche ARMv8.0 cuando haya una nueva versión de DroidDeck-Proton.
