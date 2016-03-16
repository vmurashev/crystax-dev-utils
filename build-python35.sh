#!/bin/bash -e
DIR_HERE=$(cd $(dirname $0) && pwd)
. $DIR_HERE/ndk.pth
DIR_EXTERNALS=$DIR_HERE/externals
DIR_OBJ_ROOT=$DIR_HERE/obj

mkdir -p $DIR_EXTERNALS
mkdir -p $DIR_OBJ_ROOT

PYTHON_URL='https://www.python.org/ftp/python/3.5.1/Python-3.5.1.tar.xz'
PYTHON_ARC_NAME=$(basename $PYTHON_URL)

SRC_DIR=$DIR_EXTERNALS/python35
OBJ_DIR=$DIR_OBJ_ROOT/python35

if [ ! -d $SRC_DIR ]; then
    if [ ! -f "$DIR_EXTERNALS/$PYTHON_ARC_NAME" ]; then
        curl  -L -o "$DIR_EXTERNALS/$PYTHON_ARC_NAME" $PYTHON_URL
    fi
    mkdir -p $SRC_DIR
    tar xvf "$DIR_EXTERNALS/$PYTHON_ARC_NAME" --strip-components=1 -C $SRC_DIR
fi

ABI_ALL='armeabi,armeabi-v7a,x86,mips,armeabi-v7a-hard,arm64-v8a,x86_64,mips64'
ABI_BUILD=$ABI_ALL
#ABI_BUILD=armeabi-v7a

$NDK_DIR/build/tools/build-target-python.sh --verbose --abis=$ABI_BUILD --build-dir=$OBJ_DIR $SRC_DIR

