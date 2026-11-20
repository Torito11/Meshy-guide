# Evidencias

| Archivo | Contenido |
|---|---|
| `isa_scan.py` | Escáner: desensambla con `llvm-objdump` y cuenta instrucciones que un núcleo ARMv8.0 (Cortex-A53/A73) no ejecuta. Una instrucción LSE dentro de un *helper* de *outline atomics* (`__aarch64_*`, o precedida de `cbz w16` tras leer el flag de HWCAP) se cuenta como "protegida". |
| `steam-arm64-isa.txt` | Cliente Steam ARM64 de Valve (versión 1793740892): miles de atomics LSE sin protección y el desensamblado de `ThreadInterlockedIncrement`. **Causa del error 132.** |
| `ge-proton-aarch64-isa.txt` | GE-Proton11-7-aarch64: `wineserver`, `ntdll`, `kernelbase` y DXVK con LSE sin protección. |
| `droiddeck-0.7.1-apk-isa.txt` | Los 75 ELF ARM64 de la APK oficial 0.7.1. |
| `droiddeck-0.7.1-sd685-apk-isa.txt` | Lo mismo para la APK modificada (mismo resultado). |
| `verificacion-apk.txt` | Verificación de la APK final: paquete, etiqueta, *authorities*, firma, zipalign, comprobaciones de release del proyecto, cambios presentes y diferencias con la oficial. |
| `reproducibilidad-build-referencia.txt` | APK oficial 0.7.1 frente a mi compilación **sin** cambios funcionales: mismos 596 archivos, 576 idénticos byte a byte; difieren solo `.dex`, perfiles y 15 `.so` compilados localmente. |

## Cómo leer los escaneos

- Lo determinante son las **atomics LSE sin protección**: son instrucciones de código normal.
- Los avisos RCPC2 / FCMA / SVE que aparecen dentro de funciones de OpenSSL/BoringSSL
  (`gcm_ghash_v8`, `sha1_block_data_order`, `sha512_block_data_order`, `bn_mul_mont`) y similares son
  **tablas de constantes** incrustadas en `.text` que el desensamblador interpreta como instrucciones;
  no son código ejecutado. Tampoco cuentan los de `libjingle_peerconnection_so.so` (WebRTC elige sus
  rutas *dotprod* en tiempo de ejecución).
- `libsyncthingnative.so` (Go) aparece con LSE "sin protección" porque Go comprueba su propio flag de CPU
  con otro patrón (`ldrb w2, [flag]; tbz w2, #0, ...` justo antes del `ldaddal`), que el escáner no
  reconoce. Está comprobado a mano: sí está protegido.
