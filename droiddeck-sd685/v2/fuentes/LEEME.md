# Código fuente v2

`DroidDeck-0.7.1-sd685.2-src.tar.gz`: proyecto completo de la v2 (rama `sd685-optimization`, commit
`650d3bb`; parches `../../patches/0001–0008` + `../patches/0009–0012` sobre la etiqueta oficial `0.7.1`).
Como en la v1, excluye solo los GIF/vídeos/imágenes de documentación (`docs/media`, `docs/releases/media`,
`docs/images`, `artwork`, `output`), que no intervienen en la compilación.

Compilar: `../../build/rebuild.sh` aplica `0001–0008`; después `git am ../patches/*.patch` y

    ./gradlew :app:assembleRelease -PndkVersion=27.3.13750724 \
        -PaddonPackPins=tools/sd685/addon-packs-0.7.1.properties \
        -PreleaseApplicationIdSuffix=.sd685 -PreleaseVersionNameSuffix=-sd685.2

Regenerar el parche de Proton para otra versión de DroidDeck-Proton:

    python3 tools/armv80/rewrite_tree.py <Proton original> <salida> <parche.lse80>

Copias de seguridad: v1 en `../../fuentes/DroidDeck-0.7.1-sd685-src.tar.gz`, original en
`../../fuentes/DroidDeck-0.7.1-original-src.tar.gz`.
