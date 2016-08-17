#!/bin/bash -e
DIR_HERE=$(cd $(dirname $0) && pwd)

NDK_LANDMARK="$DIR_HERE/ndk.pth"
if [ ! -f "$NDK_LANDMARK" ]; then
    echo "File with NDK landmark '$NDK_LANDMARK' not found."
    echo "NDK location should be bootstaped first."
    exit 1
fi

. $NDK_LANDMARK

PREBUILTS_ROOT="$NDK_DIR/../prebuilts/gcc/linux-x86/host"
mkdir -p "$PREBUILTS_ROOT"
PREBUILTS_ROOT=$(cd $PREBUILTS_ROOT && pwd)

MINGW_DIR="$PREBUILTS_ROOT/x86_64-w64-mingw32-4.9.3"
if [ ! -d "$MINGW_DIR" ]; then
    mkdir -p "$MINGW_DIR"
    (\
        cd "$MINGW_DIR" && \
        git clone 'https://github.com/crystax/android-platform-prebuilts-gcc-linux-x86-host-x86_64-w64-mingw32-4-9-3.git' . \
    )
else
    echo "found: $MINGW_DIR"
fi
