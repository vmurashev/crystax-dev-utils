#!/bin/bash -e

DIR_HERE=$(cd $(dirname $0) && pwd)
. $DIR_HERE/ndk.pth
DIR_EXTERNALS=$DIR_HERE/externals
DIR_OBJ_ROOT=$DIR_HERE/obj

mkdir -p $DIR_EXTERNALS
mkdir -p $DIR_OBJ_ROOT

# https://github.com/boostorg/python.git
BOOST_URL='http://downloads.sourceforge.net/project/boost/boost/1.61.0/boost_1_61_0.tar.gz'
BOOST_ARC_NAME=$(basename $BOOST_URL)
SRC_DIR="$DIR_EXTERNALS/boost"

OBJ_DIR2="$DIR_OBJ_ROOT/bpt2"
OBJ_DIR3="$DIR_OBJ_ROOT/bpt3"

if [ ! -d $SRC_DIR ]; then
    if [ ! -f "$DIR_EXTERNALS/$BOOST_ARC_NAME" ]; then
        curl  -L -o "$DIR_EXTERNALS/$BOOST_ARC_NAME" $BOOST_URL
    fi
    mkdir -p $SRC_DIR
    echo "Unpack: '$DIR_EXTERNALS/$BOOST_ARC_NAME' in '$SRC_DIR'"
    tar xf "$DIR_EXTERNALS/$BOOST_ARC_NAME" --strip-components=1 -C $SRC_DIR
fi

mkdir -p "$OBJ_DIR2"
mkdir -p "$OBJ_DIR3"

$NDK_PYTHON3 "$DIR_HERE/gen-boost-python-tests.py" \
    --jamfiles "$SRC_DIR/libs/python/test/Jamfile.v2" \
    --objdir-py2 "OBJ_DIR2"
#   --objdir-py3 "OBJ_DIR3"

echo "ERROR: BASH - TODO!"
exit 1