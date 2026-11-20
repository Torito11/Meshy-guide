# Código fuente

| Archivo | Contenido |
|---|---|
| `DroidDeck-0.7.1-original-src.tar.gz` | **Copia de seguridad del original**: DroidDeck 0.7.1 (etiqueta `0.7.1`, commit `cdff94e72c45`), sin modificar. |
| `DroidDeck-0.7.1-sd685-src.tar.gz` | **Proyecto modificado** (rama `sd685-optimization`, todos los parches de `../patches` aplicados). |

Ambos excluyen solo los GIF/vídeos/imágenes de documentación (`docs/media`, `docs/releases/media`,
`docs/images`, `artwork`, `output`), que pesan ~210 MB y no intervienen en la compilación. El original
completo está en la etiqueta pública `0.7.1` de https://github.com/Droid-Deck/DroidDeck.

Para compilar el proyecto modificado usa `../build/rebuild.sh` (parte del clon oficial completo y aplica
los parches) o, dentro del tar extraído, inicializa un repositorio git y sigue los pasos de ese script
(el submódulo `external/MaliBridge` se descarga aparte).
