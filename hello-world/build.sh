#!/bin/bash -e
DIR_HERE=$(cd $(dirname $0) && pwd)
. $DIR_HERE/../ndk.pth

ABI_BUILD='armeabi,armeabi-v7a,x86,mips,armeabi-v7a-hard,arm64-v8a,x86_64,mips64'

for abi in $(echo $ABI_BUILD | tr ',' ' '); do
    case $abi in
        x86|armeabi*|mips)
            EXE_PLATFORM=android-16
            ;;
        x86_64|arm64-v8a|mips64)
            EXE_PLATFORM=android-21
            ;;
    esac

    $NDK_DIR/ndk-build -C $DIR_HERE APP_ABI=$abi V=1 APP_LIBCRYSTAX=static APP_PLATFORM=$EXE_PLATFORM APP_PIE=true
done

echo "Done!"
