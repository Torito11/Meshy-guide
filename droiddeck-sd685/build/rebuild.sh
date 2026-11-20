#!/usr/bin/env bash
# Rebuilds DroidDeck 0.7.1-sd685 from the public upstream source plus the patches in ../patches.
#
# Needs: git, curl, zstd, unzip, python3, Java 17+, the Android SDK with platforms;android-34,
# build-tools;35.0.0, ndk;27.3.13750724 and cmake;3.22.1 (ANDROID_HOME), and Rust via rustup with
# the aarch64-linux-android target and cargo-ndk.
#
#   ./rebuild.sh [work dir]          -> <work dir>/DroidDeck/app/build/outputs/apk/release/app-release.apk
set -euo pipefail

here=$(cd "$(dirname "$0")" && pwd)
patches=$here/../patches
work=${1:-$PWD/droiddeck-sd685-build}
official_apk_url=https://github.com/Droid-Deck/DroidDeck/releases/download/0.7.1/DroidDeck-0.7.1.apk
official_apk_sha256=179ab8b4dc8f9223b70a1e4287c55a090b36ee376242186a60211100158462f1
: "${ANDROID_HOME:?set ANDROID_HOME to the Android SDK}"

mkdir -p "$work"
cd "$work"
if [ ! -d DroidDeck/.git ]; then
    git clone --branch 0.7.1 --depth 1 https://github.com/Droid-Deck/DroidDeck DroidDeck
fi
cd DroidDeck
test "$(git rev-parse HEAD)" = cdff94e72c45da50af43bbceff28effaf0179caf
git switch -c sd685-optimization 2>/dev/null || git switch sd685-optimization
if ! git log --oneline | grep -q 'stage an official release'; then
    git -c user.name=rebuild -c user.email=rebuild@localhost am "$patches"/*.patch
fi
git submodule update --init --depth 1 external/MaliBridge
printf 'sdk.dir=%s\n' "$ANDROID_HOME" > local.properties

# The unmodified native inputs come from the official 0.7.1 APK, built from this same commit.
if ! echo "$official_apk_sha256  ../DroidDeck-0.7.1.apk" | sha256sum -c --quiet 2>/dev/null; then
    curl -fL --retry 4 -o ../DroidDeck-0.7.1.apk "$official_apk_url"
    echo "$official_apk_sha256  ../DroidDeck-0.7.1.apk" | sha256sum -c --quiet
fi
bash tools/sd685/stage_release_inputs.sh ../DroidDeck-0.7.1.apk
python3 tools/release/runtime_inputs.py record

export PATH="$HOME/.cargo/bin:$PATH"
./gradlew :app:assembleRelease --console=plain \
    -PndkVersion=27.3.13750724 \
    -PaddonPackPins=tools/sd685/addon-packs-0.7.1.properties \
    -PreleaseApplicationIdSuffix=.sd685

apk=app/build/outputs/apk/release/app-release.apk
python3 tools/release/check_session_assets.py "$apk"
"$ANDROID_HOME/build-tools/35.0.0/apksigner" verify --print-certs "$apk"
sha256sum "$apk"
