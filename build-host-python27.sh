#!/bin/bash -e

if [ "$(uname -s)" = "Darwin" ]; then
    SYSTEMS_ALL='darwin-x86,darwin-x86_64'
    export PATH="$(brew --prefix coreutils)/libexec/gnubin:/usr/local/bin/:$PATH"
else
    SYSTEMS_ALL='linux-x86,linux-x86_64,windows,windows-x86_64'
fi

SYSTEMS_TO_BUILD=$SYSTEMS_ALL
#SYSTEMS_TO_BUILD='linux-x86_64'

DIR_HERE=$(cd $(dirname $0) && pwd)
. $DIR_HERE/ndk.pth
DIR_EXTERNALS=$DIR_HERE/externals
DIR_OBJ_ROOT=$DIR_HERE/obj

mkdir -p $DIR_EXTERNALS
mkdir -p $DIR_OBJ_ROOT

PYTHON_URL='https://api.github.com/repos/crystax/android-vendor-python-2-7/tarball/master'
PYTHON_ARC_NAME='vendor-host-python27.tgz'
SRC_DIR="$DIR_EXTERNALS/vendor-host-python27"
OBJ_DIR="$DIR_OBJ_ROOT/vendor-host-python27"

if [ ! -d $SRC_DIR ]; then
    if [ ! -f "$DIR_EXTERNALS/$PYTHON_ARC_NAME" ]; then
        curl  -L -o "$DIR_EXTERNALS/$PYTHON_ARC_NAME" $PYTHON_URL
    fi
    mkdir -p $SRC_DIR
    tar xvf "$DIR_EXTERNALS/$PYTHON_ARC_NAME" --strip-components=1 -C $SRC_DIR
fi

# $1: system
build_host_python ()
{
    local SYSTEM=$1
    local SYS_OPTIONS=""
    case $SYSTEM in
        windows-x86_64)
            SYS_OPTIONS="--mingw --try-64"
            ;;
        windows*)
            SYS_OPTIONS="--mingw"
            ;;
    esac

    $NDK_DIR/build/tools/build-vendor-host-python.sh --verbose \
        --systems=$SYSTEM $SYS_OPTIONS \
        --build-dir=$OBJ_DIR --package-dir="$DIR_HERE/pkg" \
        $SRC_DIR
}

for system in $(echo $SYSTEMS_TO_BUILD | tr ',' ' '); do
    build_host_python $system
done
