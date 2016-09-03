#!/bin/bash -e

DIR_HERE=$(cd $(dirname $0) && pwd)
. $DIR_HERE/ndk.pth
DIR_EXTERNALS=$DIR_HERE/externals
DIR_OBJ_ROOT=$DIR_HERE/obj

mkdir -p $DIR_EXTERNALS
mkdir -p $DIR_OBJ_ROOT

# https://github.com/boostorg/python.git
BOOST_PYTHON_URL='https://api.github.com/repos/boostorg/python/tarball/master'
BOOST_PYTHON_ARC_NAME='boost-python.tgz'
SRC_DIR="$DIR_EXTERNALS/boost-python-tests"

if [ ! -d $SRC_DIR ]; then
    if [ ! -f "$DIR_EXTERNALS/$BOOST_PYTHON_ARC_NAME" ]; then
        curl  -L -o "$DIR_EXTERNALS/$BOOST_PYTHON_ARC_NAME" $BOOST_PYTHON_URL
    fi
    FLIST=$(tar -tf $DIR_EXTERNALS/$BOOST_PYTHON_ARC_NAME | grep '/test/..*' | tr '\n' ' ')
    mkdir -p $SRC_DIR
    tar xvf "$DIR_EXTERNALS/$BOOST_PYTHON_ARC_NAME" --strip-components=2 -C $SRC_DIR $FLIST
fi

echo "ERROR: TODO!"