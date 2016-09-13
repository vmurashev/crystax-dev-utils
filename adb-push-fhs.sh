#!/bin/bash -e
DIR_HERE=$(cd $(dirname $0) && pwd)
. $DIR_HERE/ndk.pth
$NDK_PYTHON3 "$DIR_HERE/adb-push-fhs-impl.py" "$@"
