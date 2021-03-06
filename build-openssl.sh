#!/bin/bash -e

DIR_HERE=$(cd $(dirname $0) && pwd)
. $DIR_HERE/ndk.pth
DIR_EXTERNALS=$DIR_HERE/externals
DIR_OBJ_ROOT=$DIR_HERE/obj

mkdir -p $DIR_EXTERNALS
mkdir -p $DIR_OBJ_ROOT

OPENSSL_VERSION='1.0.2h'
OPENSSL_URL="ftp://ftp.openssl.org/source/openssl-$OPENSSL_VERSION.tar.gz"
OPENSSL_ARC_NAME=$(basename $OPENSSL_URL)

SRC_DIR=$DIR_EXTERNALS/"openssl-$OPENSSL_VERSION"
OBJ_DIR=$DIR_OBJ_ROOT/"openssl-$OPENSSL_VERSION"

if [ ! -d $SRC_DIR ]; then
    if [ ! -f "$DIR_EXTERNALS/$OPENSSL_ARC_NAME" ]; then
        curl -L -o "$DIR_EXTERNALS/$OPENSSL_ARC_NAME" $OPENSSL_URL
    fi
    mkdir -p $SRC_DIR
    tar xvf "$DIR_EXTERNALS/$OPENSSL_ARC_NAME" --strip-components=1 -C $SRC_DIR
fi

ABI_ALL='armeabi,armeabi-v7a,armeabi-v7a-hard,x86,mips,arm64-v8a,x86_64,mips64'
ABI_BUILD=$ABI_ALL
#ABI_BUILD=armeabi-v7a

$NDK_DIR/build/instruments/build-target-openssl.sh --verbose --abis=$ABI_BUILD --build-dir=$OBJ_DIR $SRC_DIR
