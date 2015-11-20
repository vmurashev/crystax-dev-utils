#!/bin/bash -e
DIR_HERE=$(cd $(dirname $0) && pwd)
CERTDATA_URL='https://certifi-bundles.s3.amazonaws.com/latest.pem'
CERTDATA_LOCAL="$DIR_HERE/certdata.pem"

if [ -f "$CERTDATA_LOCAL" ]; then
    rm -rf $CERTDATA_LOCAL
fi

echo "Downloading $CERTDATA_URL ..."
curl  -L -o $CERTDATA_LOCAL $CERTDATA_URL

