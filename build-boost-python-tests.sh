#!/bin/bash -e

DIR_HERE=$(cd $(dirname $0) && pwd)
. $DIR_HERE/ndk.pth
. $DIR_HERE/ndk-py3.pth
DIR_EXTERNALS=$DIR_HERE/externals
DIR_OBJ_ROOT=$DIR_HERE/obj

mkdir -p $DIR_EXTERNALS
mkdir -p $DIR_OBJ_ROOT

BOOST_URL='https://api.github.com/repos/vmurashev/android-vendor-boost-1-62-0/tarball/develop'
BOOST_VERSION='1.62.0'
BOOST_ARC_NAME="boost-$BOOST_VERSION.tgz"


SRC_DIR="$DIR_EXTERNALS/boost/$BOOST_VERSION"

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


OBJ_DIR2="$DIR_OBJ_ROOT/bpt2"
OBJ_DIR3="$DIR_OBJ_ROOT/bpt3"

mkdir -p "$OBJ_DIR2"
mkdir -p "$OBJ_DIR3"

BUILD_STAMP_PY2="$OBJ_DIR2/build.stamp"
BUILD_STAMP_PY3="$OBJ_DIR3/build.stamp"

PACK_STAMP_PY2="$OBJ_DIR2/pack.stamp"
PACK_STAMP_PY3="$OBJ_DIR3/pack.stamp"

BUILD_DIRS_FILE_PY2="$OBJ_DIR2/build-items.txt"
BUILD_DIRS_FILE_PY3="$OBJ_DIR3/build-items.txt"

if [ -d "$OBJ_DIR2" ]; then
    if [ ! -f "$BUILD_STAMP_PY2" ]; then
        $NDK_PYTHON3 "$DIR_HERE/gen-boost-python-tests.py" --jamfiles "$SRC_DIR/libs/python/test/Jamfile.v2" --objdir-py2 "$OBJ_DIR2" --boost-version "$BOOST_VERSION"

        if [ -f $BUILD_DIRS_FILE_PY2 ]; then
            DNAMES2=$(cat $BUILD_DIRS_FILE_PY2)
            for dname in $DNAMES2; do
                MY_SRC_DIR="$OBJ_DIR2/$dname"
                $NDK_DIR/ndk-build -C $MY_SRC_DIR APP_ABI=$ABI_BUILD V=1
            done
        fi
        touch "$BUILD_STAMP_PY2"
    fi
    if [ ! -f "$PACK_STAMP_PY2" ]; then
        for abi in $(echo $ABI_BUILD | tr ',' ' '); do
            $NDK_PYTHON3 "$DIR_HERE/pack-boost-python-tests.py" --target-python python2 \
                --objdir "$OBJ_DIR2" --abi $abi --tgzout "$DIR_OBJ_ROOT/bpt2-$abi.tgz"
        done
        touch "$PACK_STAMP_PY2"
    fi
fi

if [ -d "$OBJ_DIR3" ]; then
    if [ ! -f "$BUILD_STAMP_PY3" ]; then
        $NDK_PYTHON3 "$DIR_HERE/gen-boost-python-tests.py" --jamfiles "$SRC_DIR/libs/python/test/Jamfile.v2" --objdir-py3 "$OBJ_DIR3" --boost-version "$BOOST_VERSION"

        if [ -f $BUILD_DIRS_FILE_PY3 ]; then
            DNAMES3=$(cat $BUILD_DIRS_FILE_PY3)
            for dname in $DNAMES3; do
                MY_SRC_DIR="$OBJ_DIR3/$dname"
                $NDK_DIR/ndk-build -C $MY_SRC_DIR APP_ABI=$ABI_BUILD V=1
            done
        fi
        touch "$BUILD_STAMP_PY3"
    fi
    if [ ! -f "$PACK_STAMP_PY3" ]; then
        for abi in $(echo $ABI_BUILD | tr ',' ' '); do
            $NDK_PYTHON3 "$DIR_HERE/pack-boost-python-tests.py" --target-python python3 \
                --objdir "$OBJ_DIR3" --abi $abi --tgzout "$DIR_OBJ_ROOT/bpt3-$abi.tgz"
        done
        touch "$PACK_STAMP_PY3"
    fi
fi
