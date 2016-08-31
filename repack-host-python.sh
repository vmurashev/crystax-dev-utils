#!/bin/bash -e
DIR_HERE=$(cd $(dirname $0) && pwd)

DIR_SRC=/var/tmp/ndk-cache-$USER

if [ ! -d "$DIR_SRC" ]; then
    echo "Directory not found - $DIR_SRC"
    exit 0
fi

OUTPUT=$DIR_SRC/repack
rm -rf $OUTPUT && mkdir -p $OUTPUT

for filename in $DIR_SRC/*.tar.xz; do
    case $filename in
        *vendor-host-python*windows*)
                base="${filename%.*}"
                base="${base%.*}"
                rm -rf $base && mkdir -p $base
                rm -rf $base.zip
                tar xf $filename --strip-components=3 -C $base
                (cd $base && zip -r "$base.zip" .)
                rm -rf $base
                ret=$(basename "$base.zip")
                ret="${ret#ndk-vendor-host-}"
                ret=$OUTPUT/$ret
                mv $base.zip $ret
                echo "done - $ret"
            ;;
        *vendor-host-python*)
                base="${filename%.*}"
                base="${base%.*}"
                rm -rf $base && mkdir -p $base
                rm -rf $base.tgz
                tar xf $filename --strip-components=3 -C $base
                (cd $base && tar cvzf "$base.tgz" .)
                rm -rf $base
                ret=$(basename "$base.tgz")
                ret="${ret#ndk-vendor-host-}"
                ret=$OUTPUT/$ret
                mv $base.tgz $ret
                echo "done - $ret"
            ;;
    esac
done
