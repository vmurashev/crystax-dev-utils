#!/bin/bash -e
DIR_HERE=$(cd $(dirname $0) && pwd)

DOWNLOAD_DIR=$DIR_HERE/downloads
mkdir -p $DOWNLOAD_DIR

if [ "$(uname -s)" = "Darwin" ] ; then
    CRYSTAX_LATEST_BUILD_URL="https://dl.crystax.net/ndk/darwin/latest"
else
    CRYSTAX_LATEST_BUILD_URL="https://dl.crystax.net/ndk/linux/latest"
fi
CRYSTAX_LATEST_BUILD_FILE="$DOWNLOAD_DIR/crystax.latest-build"
CRYSTAX_LATEST_BUILD_FILE_TMP=$CRYSTAX_LATEST_BUILD_FILE".tmp"
rm -f $CRYSTAX_LATEST_BUILD_FILE_TMP
echo "downloading $CRYSTAX_LATEST_BUILD_URL ..."
curl  -L -o $CRYSTAX_LATEST_BUILD_FILE_TMP $CRYSTAX_LATEST_BUILD_URL

CRYSTAX_LAST_DWNL_BUILD='<unknown>'
CRYSTAX_LATEST_BUILD=$(cat $CRYSTAX_LATEST_BUILD_FILE_TMP)
if [ -f $CRYSTAX_LATEST_BUILD_FILE ]; then
    CRYSTAX_LAST_DWNL_BUILD=$(cat $CRYSTAX_LATEST_BUILD_FILE)
fi
echo "crystax last downloaded build: '$CRYSTAX_LAST_DWNL_BUILD'"
echo "crystax latest build: '$CRYSTAX_LATEST_BUILD'"
if [ "$CRYSTAX_LAST_DWNL_BUILD" = "$CRYSTAX_LATEST_BUILD" ]; then
    echo "Nothing to do: latest build '$CRYSTAX_LATEST_BUILD' already downloaded"
    exit 0
fi

if [ "$(uname -s)" = "Darwin" ] ; then
    CRYSTAX_BUILDINFO_URL="https://dl.crystax.net/ndk/darwin/$CRYSTAX_LATEST_BUILD/checksum-darwin.sha256"
else
    CRYSTAX_BUILDINFO_URL="https://dl.crystax.net/ndk/linux/$CRYSTAX_LATEST_BUILD/checksum-linux.sha256"
fi
CRYSTAX_BUILDINFO_FILE="$DOWNLOAD_DIR/crystax.buildinfo-$CRYSTAX_LATEST_BUILD"

if [ ! -f $CRYSTAX_BUILDINFO_FILE ]; then
    echo "downloading $CRYSTAX_BUILDINFO_URL ..."
    curl  -L -o $CRYSTAX_BUILDINFO_FILE $CRYSTAX_BUILDINFO_URL
fi

if [ "$(uname -s)" = "Darwin" ]; then
    CRYSTAX_DISTR_NAME=$(grep -e -x86_64\\. < $CRYSTAX_BUILDINFO_FILE | tr '()' '"' | grep -o '\".*\"' | tr -d '"')
    CRYSTAX_URL="https://dl.crystax.net/ndk/darwin/$CRYSTAX_LATEST_BUILD/$CRYSTAX_DISTR_NAME"
else
    if [ -n "$(uname -m | grep 64)" ]; then
        CRYSTAX_DISTR_NAME=$(grep -e -x86_64\\. < $CRYSTAX_BUILDINFO_FILE | tr '()' '"' | grep -o '\".*\"' | tr -d '"')
    else
        CRYSTAX_DISTR_NAME=$(grep -e -x86\\. < $CRYSTAX_BUILDINFO_FILE | tr '()' '"' | grep -o '\".*\"' | tr -d '"')
    fi
    CRYSTAX_URL="https://dl.crystax.net/ndk/linux/$CRYSTAX_LATEST_BUILD/$CRYSTAX_DISTR_NAME"
fi

CRYSTAX_TARGET_ARC="$DOWNLOAD_DIR/$CRYSTAX_LATEST_BUILD/crystax-ndk.tar.xz"
echo "crystax url: '$CRYSTAX_URL'"
echo "download target: '$CRYSTAX_TARGET_ARC'"

mkdir -p $(dirname $CRYSTAX_TARGET_ARC)
if [ -f $CRYSTAX_TARGET_ARC ]; then
  echo "Already downloaded"
else
  echo "Downloading $CRYSTAX_URL ..."
  curl  -L -o $CRYSTAX_TARGET_ARC $CRYSTAX_URL
fi
mv $CRYSTAX_LATEST_BUILD_FILE_TMP $CRYSTAX_LATEST_BUILD_FILE
