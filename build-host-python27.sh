#!/bin/bash -e
DIR_HERE=$(cd $(dirname $0) && pwd)
. $DIR_HERE/ndk.pth
DIR_EXTERNALS=$DIR_HERE/externals
DIR_OBJ_ROOT=$DIR_HERE/obj

mkdir -p $DIR_EXTERNALS
mkdir -p $DIR_OBJ_ROOT

PYTHON_URL='https://api.github.com/repos/crystax/android-toolchain-python/tarball/master'
PYTHON_ARC_NAME='android-toolchain-python27.tgz'

SRC_DIR="$DIR_EXTERNALS/host-python27"

if [ ! -d $SRC_DIR ]; then
    if [ ! -f "$DIR_EXTERNALS/$PYTHON_ARC_NAME" ]; then
        curl  -L -o "$DIR_EXTERNALS/$PYTHON_ARC_NAME" $PYTHON_URL
    fi
    mkdir -p $SRC_DIR
    tar xvf "$DIR_EXTERNALS/$PYTHON_ARC_NAME" --strip-components=2 -C $SRC_DIR
fi

SYSTEMS_ALL='linux-x86,linux-x86_64,windows,windows-x86_64'

for system in $(echo $SYSTEMS_ALL | tr ',' ' '); do
    rm -f "/var/tmp/ndk-cache-$USER/ndk-python-$system.tar.xz"
done

# $1: system
build_host_python ()
{
    local SYSTEM=$1
    local OBJ_SYS_DIR="$DIR_OBJ_ROOT/host-python27-$SYSTEM"
    local SYS_OPTIONS=""
    case $SYSTEM in
        windows-x86_64)
            SYS_OPTIONS="--mingw"
            ;;
        windows-x86_64)
            SYS_OPTIONS="--mingw --try-64"
            ;;
    esac

    rm -rf $OBJ_SYS_DIR
    local OBJ_DIR="$OBJ_SYS_DIR/0"
    local PKG_DIR="$OBJ_SYS_DIR/pkg"
    $NDK_DIR/build/tools/build-host-python.sh --verbose \
        --build-dir=$OBJ_DIR --systems=$SYSTEM $SYS_OPTIONS --package-dir=$PKG_DIR $SRC_DIR
}

SYSTEMS_TO_BUILD=$SYSTEMS_ALL
#SYSTEMS_TO_BUILD='windows-x86_64'

for system in $(echo $SYSTEMS_TO_BUILD | tr ',' ' '); do
    build_host_python $system
done
