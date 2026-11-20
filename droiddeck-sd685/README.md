# DroidDeck 0.7.1-sd685 — versión para Redmi Note 13 (Snapdragon 685 / Adreno 610)

Versión modificada de [DroidDeck](https://github.com/Droid-Deck/DroidDeck) 0.7.1 (GPL-3.0) que corrige el
cierre de Steam con **error 132** en CPUs ARMv8.0 y añade un perfil para hardware de gama baja.

## En una frase

Steam se cerraba porque el **cliente Steam ARM64 de Valve usa instrucciones ARMv8.1 (atomics LSE) que tu
CPU no tiene** — lo comprobé desensamblando el binario. Esta versión usa automáticamente el cliente Steam
x86-64 bajo el traductor FEX (que sí funciona en ARMv8.0) y evita también Proton ARM64, que fallaría igual
con cualquier juego de Windows.

## Contenido

| Archivo | Qué es |
|---|---|
| [`DIAGNOSTICO.md`](DIAGNOSTICO.md) | Análisis completo de los registros, causa raíz demostrada y lo que no era la causa |
| [`CAMBIOS.md`](CAMBIOS.md) | Registro detallado de cada modificación |
| [`PRUEBAS.md`](PRUEBAS.md) | Informe de pruebas: qué se probó, resultados y qué no se pudo probar |
| [`INSTALACION.md`](INSTALACION.md) | Instalación, primer uso, ajustes recomendados, actualización y cómo volver atrás |
| [`COMPATIBILIDAD.md`](COMPATIBILIDAD.md) | Qué juegos pueden funcionar, Steam vs Xbox Cloud, límites del hardware |
| `apk/` | La APK compilada y su `SHA256SUMS` |
| `patches/` | Las modificaciones como parches `git am` sobre la etiqueta oficial `0.7.1` |
| `build/rebuild.sh` | Reconstrucción reproducible desde el código oficial + parches |
| `evidencia/` | Escaneos de instrucciones de los binarios (Steam ARM64, GE-Proton aarch64, APK) y el escáner |

## Resumen de cambios

1. **Cliente Steam x86-64 automático** en CPUs sin LSE (detección por `HWCAP_ATOMICS` del kernel).
2. **Juegos de Windows con Proton x86-64 de Valve bajo FEX** (`droiddeck-proton-x64`, sin contenedor) en
   lugar de Proton ARM64; sin descargas inútiles de Proton/cliente ARM64.
3. **Perfil de gama baja**: sesión a 60 Hz por defecto (ajustable), xCloud nativo sin DDFG por defecto.
4. **Mensajes y diagnóstico** que nombran la causa real.
5. Textos en español de España y de Latinoamérica.

Las funciones originales se conservan (Xbox, tiendas, escritorio, etc.). No requiere root.

## Importante

- Se instala **junto** a tu DroidDeck oficial, como "DroidDeck SD685" (`com.droiddeck.launcher.sd685`):
  la APK oficial está firmada con la clave privada del proyecto y Android no deja que otra firma la
  actualice. Así **tus datos actuales no se tocan**. Detalles en `INSTALACION.md`.
- **No he podido probarla en un teléfono** (ni en emulador: este entorno no tiene KVM). Está compilada,
  firmada, verificada y con tests automáticos en verde, pero el funcionamiento real de Steam x86-64 y de
  Proton x86-64 en tu Redmi Note 13 está sin confirmar. Ver `PRUEBAS.md`.
- Para jugar a títulos de Xbox/Game Pass en este móvil, la vía realista es **Xbox Cloud Gaming**.

## Copia de seguridad del original

- Código original: etiqueta pública `0.7.1` de github.com/Droid-Deck/DroidDeck (commit `cdff94e72c45da50af43bbceff28effaf0179caf`).
- APK original: `DroidDeck-0.7.1.apk` de las releases oficiales, SHA-256 `179ab8b4dc8f9223b70a1e4287c55a090b36ee376242186a60211100158462f1`.
- Se entregan además los archivos `DroidDeck-0.7.1-original-src.tar.gz` y `DroidDeck-0.7.1-sd685-src.tar.gz`
  (código sin los GIF/vídeos de la documentación).

Licencia: GPL-3.0, como el proyecto original. Steam y Proton son de Valve; Xbox es de Microsoft. Proyecto
no afiliado a ninguno de ellos.
