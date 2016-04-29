#!/bin/bash -e
DIR_HERE=$(cd $(dirname $0) && pwd)
. $DIR_HERE/ndk.pth

ABI_ALL='armeabi,armeabi-v7a,x86,mips,armeabi-v7a-hard,arm64-v8a,x86_64,mips64'
ABI_BUILD=$ABI_ALL
#ABI_BUILD=armeabi-v7a

$DIR_HERE/mkpyzip.py --src-root "$DIR_HERE/python-world/six" --out "$DIR_HERE/obj/mkpyzip/six.zip"

for abi in $(echo $ABI_BUILD | tr ',' ' '); do
    cp -p -T "$DIR_HERE/obj/mkpyzip/six.zip" "$NDK_DIR/sources/python/3.5/shared/$abi/site-packages/six.zip"
done

echo "Done!"
