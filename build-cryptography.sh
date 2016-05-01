#!/bin/bash -e
DIR_HERE=$(cd $(dirname $0) && pwd)
. $DIR_HERE/ndk.pth

ABI_ALL='armeabi,armeabi-v7a,x86,mips,armeabi-v7a-hard,arm64-v8a,x86_64,mips64'
ABI_BUILD=$ABI_ALL
#ABI_BUILD=armeabi-v7a

$NDK_DIR/ndk-build -C "$DIR_HERE/python-world/cryptography" APP_ABI=$ABI_BUILD V=1
$DIR_HERE/mkpyzip.py --src "$DIR_HERE/python-world/cryptography/cryptography" --out "$DIR_HERE/obj/mkpyzip/cryptography.zip"

for abi in $(echo $ABI_BUILD | tr ',' ' '); do
    cp -p -T "$DIR_HERE/python-world/cryptography/obj/local/$abi/lib_cryptography_constant_time.so" \
        "$NDK_DIR/sources/python/3.5/shared/$abi/site-packages/_cryptography_constant_time.so"

    cp -p -T "$DIR_HERE/python-world/cryptography/obj/local/$abi/lib_cryptography_openssl.so" \
        "$NDK_DIR/sources/python/3.5/shared/$abi/site-packages/_cryptography_openssl.so"

    cp -p -T "$DIR_HERE/python-world/cryptography/obj/local/$abi/lib_cryptography_padding.so" \
        "$NDK_DIR/sources/python/3.5/shared/$abi/site-packages/_cryptography_padding.so"

    cp -p -T "$DIR_HERE/obj/mkpyzip/cryptography.zip" \
        "$NDK_DIR/sources/python/3.5/shared/$abi/site-packages/cryptography.zip"
done

echo "Done!"
