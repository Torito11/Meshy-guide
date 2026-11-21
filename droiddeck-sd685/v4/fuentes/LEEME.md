# Código fuente v4

`DroidDeck-0.7.1-sd685.4-src.tar.gz`: proyecto completo (rama `sd685-optimization`, commit `65bf8f1`): la
etiqueta oficial `0.7.1` + `../../patches/0001–0008` (v1) + `../../v2/patches/0009–0012` (v2) +
`../../v3/patches/0013–0016` (v3) + `../patches/0017–0021` (v4). Excluye solo los GIF/vídeos/imágenes de
documentación, como las versiones anteriores.

Compilar (tras aplicar los parches, ver `../../build/rebuild.sh`):

    python3 tools/release/runtime_inputs.py record
    ./gradlew :app:assembleRelease -PndkVersion=27.3.13750724 \
        -PaddonPackPins=tools/sd685/addon-packs-0.7.1.properties \
        -PreleaseApplicationIdSuffix=.sd685 -PreleaseVersionNameSuffix=-sd685.4

No dejes paquetes en `app/build/packs` al compilar: se incrustarían en la APK (los paquetes fijados se
descargan y verifican en el teléfono).
