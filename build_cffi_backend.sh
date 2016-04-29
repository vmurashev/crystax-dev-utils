#!/bin/bash -e
DIR_HERE=$(cd $(dirname $0) && pwd)
. $DIR_HERE/ndk.pth

ABI_ALL='armeabi,armeabi-v7a,x86,mips,armeabi-v7a-hard,arm64-v8a,x86_64,mips64'
ABI_BUILD=$ABI_ALL
#ABI_BUILD=armeabi-v7a

$NDK_DIR/ndk-build -C "$DIR_HERE/python-world/cffi" APP_ABI=$ABI_BUILD V=1

for abi in $(echo $ABI_BUILD | tr ',' ' '); do
    cp -p -T "$DIR_HERE/python-world/cffi/obj/local/$abi/lib_cffi_backend.so" "$NDK_DIR/sources/python/3.5/shared/$abi/site-packages/_cffi_backend.so"
done
