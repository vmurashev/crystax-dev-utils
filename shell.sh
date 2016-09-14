#!/system/bin/sh
DIR_HERE=$(cd ${0%shell.sh} && pwd)
export LD_LIBRARY_PATH=$DIR_HERE/fhs/lib
export PATH=$PATH:$DIR_HERE/fhs/bin
cd $DIR_HERE/fhs
exec /system/bin/sh "$@"
