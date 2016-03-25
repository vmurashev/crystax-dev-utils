#!/bin/bash -e

SYSTEMS_ALL='linux-x86,linux-x86_64,windows,windows-x86_64,darwin-x86,darwin-x86_64'
SYSTEMS_TO_BUILD=$SYSTEMS_ALL
#SYSTEMS_TO_BUILD='windows'


DIR_HERE=$(cd $(dirname $0) && pwd)
. $DIR_HERE/ndk.pth
DIR_EXTERNALS=$DIR_HERE/externals
DIR_OBJ_ROOT=$DIR_HERE/obj

mkdir -p $DIR_EXTERNALS
mkdir -p $DIR_OBJ_ROOT

PYTHON_URL='https://api.github.com/repos/crystax/android-vendor-python-3-5/tarball/master'
PYTHON_ARC_NAME='vendor-host-python35.tgz'
SRC_DIR="$DIR_EXTERNALS/vendor-host-python35"

if [ ! -d $SRC_DIR ]; then
    if [ ! -f "$DIR_EXTERNALS/$PYTHON_ARC_NAME" ]; then
        curl  -L -o "$DIR_EXTERNALS/$PYTHON_ARC_NAME" $PYTHON_URL
    fi
    mkdir -p $SRC_DIR
    tar xvf "$DIR_EXTERNALS/$PYTHON_ARC_NAME" --strip-components=1 -C $SRC_DIR
fi

for system in $(echo $SYSTEMS_ALL | tr ',' ' '); do
    rm -f "/var/tmp/ndk-cache-$USER/ndk-vendor-host-python3.5-$system.tar.xz"
done

# $1: system
build_host_python ()
{
    local SYSTEM=$1
    local OBJ_SYS_DIR="$DIR_OBJ_ROOT/vendor-host-python35-$SYSTEM"
    local SYS_OPTIONS=""
    case $SYSTEM in
        windows)
            SYS_OPTIONS="--mingw"
            ;;
        windows-x86_64)
            SYS_OPTIONS="--mingw --try-64"
            ;;
    esac

    rm -rf $OBJ_SYS_DIR
    local OBJ_DIR="$OBJ_SYS_DIR/0"
    local PKG_DIR="$OBJ_SYS_DIR/pkg"
    $NDK_DIR/build/tools/build-vendor-host-python.sh --verbose \
        --systems=$SYSTEM $SYS_OPTIONS \
        --build-dir=$OBJ_DIR \
        --package-dir=$PKG_DIR $SRC_DIR
}

for system in $(echo $SYSTEMS_TO_BUILD | tr ',' ' '); do
    build_host_python $system
done
