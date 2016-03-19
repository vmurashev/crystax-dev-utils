#!/bin/bash -e
DIR_HERE=$(cd $(dirname $0) && pwd)
. $DIR_HERE/ndk.pth
DIR_EXTERNALS=$DIR_HERE/externals
DIR_OBJ_ROOT=$DIR_HERE/obj
DIR_PKG_ROOT=$DIR_HERE/pkg

mkdir -p $DIR_EXTERNALS
mkdir -p $DIR_OBJ_ROOT
mkdir -p $DIR_PKG_ROOT

PYTHON_URL='https://api.github.com/repos/crystax/android-toolchain-python/tarball/master'
PYTHON_ARC_NAME='android-toolchain-python27.tgz'

SRC_DIR="$DIR_EXTERNALS/host-python27"
OBJ_DIR="$DIR_OBJ_ROOT/host-python27"

if [ ! -d $SRC_DIR ]; then
    if [ ! -f "$DIR_EXTERNALS/$PYTHON_ARC_NAME" ]; then
        curl  -L -o "$DIR_EXTERNALS/$PYTHON_ARC_NAME" $PYTHON_URL
    fi
    mkdir -p $SRC_DIR
    tar xvf "$DIR_EXTERNALS/$PYTHON_ARC_NAME" --strip-components=2 -C $SRC_DIR
fi

SYSTEMS_ALL='linux-x86,linux-x86_64,windows,windows-x86_64,darwin-x86,darwin-x86_64'
#SYSTEMS_TO_BUILD=$SYSTEMS_ALL
SYSTEMS_TO_BUILD='linux-x86_64'

rm -rf $OBJ_DIR
for system in $(echo $SYSTEMS_TO_BUILD | tr ',' ' '); do
    rm -rf "/var/tmp/ndk-cache-$USER/ndk-python-$system.tar.xz"
    rm -rf "$DIR_PKG_ROOT/ndk-python-$system.tar.xz"
done

$NDK_DIR/build/tools/build-host-python.sh --verbose \
    --build-dir=$OBJ_DIR --systems=$SYSTEMS_TO_BUILD --package-dir=$DIR_PKG_ROOT $SRC_DIR
