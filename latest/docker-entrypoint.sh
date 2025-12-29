#!/bin/bash
set -e

mkdir -p /data/blobstorage /data/filestorage /data/cache /data/log /data/zeoserver
chown -R senaite:senaite /data || true

su senaite -c "python /docker-initialize.py"

# ZEO
if [[ "$1" == "zeo" ]]; then
  exec su senaite -c "bin/zeoserver fg"
fi

# Web
exec su senaite -c "bin/instance fg"
