#!/bin/bash -e
DIR_HERE=$(cd $(dirname $0) && pwd)

NDL_LANDMARK="$DIR_HERE/ndk.pth"
if [ ! -f "$NDL_LANDMARK" ]; then
    echo "File with NDK landmark '$NDL_LANDMARK' not found."
    echo "NDK location should bootstaped first."
    exit 1
fi

. $NDL_LANDMARK

PREBUILTS_ROOT="$NDK_DIR/../prebuilts/gcc/linux-x86/host"
mkdir -p "$PREBUILTS_ROOT"
PREBUILTS_ROOT=$(cd $PREBUILTS_ROOT && pwd)

MINGW_DIR_X86_64="$PREBUILTS_ROOT/x86_64-w64-mingw32-4.8"
if [ ! -d "$MINGW_DIR_X86_64" ]; then
    mkdir -p "$MINGW_DIR_X86_64"
    (\
        cd "$MINGW_DIR_X86_64" && \
        git clone 'https://github.com/crystax/android-platform-prebuilts-gcc-linux-x86-host-x86_64-w64-mingw32-4-8.git' . \
    )
else
    echo "found: $MINGW_DIR_X86_64"
fi

MINGW_DIR_X86="$PREBUILTS_ROOT/i686-w64-mingw32-4.8"
if [ ! -d "$MINGW_DIR_X86" ]; then
    mkdir -p "$MINGW_DIR_X86"
    (\
        cd "$MINGW_DIR_X86" && \
        git clone 'https://github.com/crystax/android-platform-prebuilts-gcc-linux-x86-host-i686-w64-mingw32-4-8.git' . \
    )
else
    echo "found: $MINGW_DIR_X86"
fi
