#!/bin/bash -e
DIR_HERE=$(cd $(dirname $0) && pwd)
DOWNLOAD_DIR=$DIR_HERE/downloads

CRYSTAX_BUILDS_ROOT="$DIR_HERE/crystax"
mkdir -p $CRYSTAX_BUILDS_ROOT
CRYSTAX_LATEST_BUILD_FILE="$DOWNLOAD_DIR/crystax.latest-build"
if [ -f $CRYSTAX_LATEST_BUILD_FILE ]; then
    CRYSTAX_LATEST_BUILD=$(cat $CRYSTAX_LATEST_BUILD_FILE)
else
    echo "File '$CRYSTAX_LATEST_BUILD_FILE' not found"
    exit 1
fi
CRYSTAX_ARC="$DOWNLOAD_DIR/$CRYSTAX_LATEST_BUILD/crystax-ndk.tar.xz"
if [ ! -f $CRYSTAX_ARC ]; then
    echo "File '$CRYSTAX_ARC' not found"
    exit 1
fi

NDK_HOME=$CRYSTAX_BUILDS_ROOT/$CRYSTAX_LATEST_BUILD
if [ "$(uname -s)" = "Darwin" ]; then
    BH_TAG='darwin-x86_64'
else
    BH_TAG='linux-x86_64'
fi

echo "NDK_DIR='$NDK_HOME/android-platform-ndk'" > "$DIR_HERE/ndk.pth"
echo "NDK_PYTHON3='$NDK_HOME/android-platform-ndk/prebuilt/$BH_TAG/opt/python3.5/python'" > "$DIR_HERE/ndk-py3.pth"

if [ -d $NDK_HOME ]; then
    echo "Already bootstraped: $NDK_HOME"
    exit 0
fi

mkdir -p "$NDK_HOME/android-platform-ndk"
cd $NDK_HOME

echo 'Clone android-platform-ndk from github.com ...'
git clone 'https://github.com/vmurashev/android-platform-ndk.git'

echo 'Merge prebuilts with devl ...'
echo "Extract $CRYSTAX_ARC in $NDK_HOME ..."
tar xf $CRYSTAX_ARC --strip-components=1 -C 'android-platform-ndk'
cd 'android-platform-ndk'
set -x
git status
git checkout --
git reset --hard
git clean -df
git status
