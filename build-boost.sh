#!/bin/bash -e

DIR_HERE=$(cd $(dirname $0) && pwd)
. $DIR_HERE/ndk.pth
DIR_EXTERNALS=$DIR_HERE/externals
DIR_OBJ_ROOT=$DIR_HERE/obj

mkdir -p $DIR_EXTERNALS
mkdir -p $DIR_OBJ_ROOT

BOOST_URL='https://api.github.com/repos/vmurashev/android-vendor-boost-1-62-0/tarball/develop'
BOOST_VERSION='1.62.0'
BOOST_ARC_NAME="boost-$BOOST_VERSION.tgz"


SRC_DIR="$DIR_EXTERNALS/boost/$BOOST_VERSION"

OBJ_DIR="$DIR_OBJ_ROOT/boost-$BOOST_VERSION"

if [ ! -d $SRC_DIR ]; then
    if [ ! -f "$DIR_EXTERNALS/$BOOST_ARC_NAME" ]; then
        curl -L -o "$DIR_EXTERNALS/$BOOST_ARC_NAME" $BOOST_URL
    fi
    mkdir -p $SRC_DIR
    tar xvf "$DIR_EXTERNALS/$BOOST_ARC_NAME" --strip-components=1 -C $SRC_DIR
fi

ABI_ALL='armeabi,armeabi-v7a,armeabi-v7a-hard,x86,mips,arm64-v8a,x86_64,mips64'
ABI_BUILD=$ABI_ALL
#ABI_BUILD=armeabi-v7a

SRC_DIR_BUILD=$(cd $SRC_DIR && cd .. && pwd)
mkdir -p $OBJ_DIR
NDK_LOGFILE=$OBJ_DIR/ndk-build.log
rm -rf $NDK_LOGFILE
export NDK_LOGFILE
$NDK_DIR/build/instruments/build-boost.sh --verbose --abis=$ABI_BUILD --version=$BOOST_VERSION --stdlibs='gnu-5' --build-dir=$OBJ_DIR $SRC_DIR_BUILD
