#!/bin/bash
set -euo pipefail

# Defaults (ajusta via HCL)
: "${HTTP_PORT:=8080}"
: "${INSTANCE_DIR:=/data/instance}"
: "${ADMIN_USER:=admin}"
: "${ADMIN_PASSWORD:=admin}"

# Diretórios comuns
mkdir -p /data/blobstorage /data/filestorage /data/cache /data/log "$INSTANCE_DIR"

# Permissões (rodar como root no container facilita; se for non-root, isso muda)
# Se você estiver usando USER senaite no Dockerfile, remova esses chown ou rode container com permissão.
chown -R senaite:senaite /data || true

# Cria instância se não existir
if [ ! -f "$INSTANCE_DIR/etc/zope.conf" ]; then
  echo "[init] Creating WSGI instance at $INSTANCE_DIR"
  su -s /bin/bash -c "mkwsgiinstance -d '$INSTANCE_DIR' -u '${ADMIN_USER}:${ADMIN_PASSWORD}'" senaite
fi

# Ajusta porta no zope.conf
CONF="$INSTANCE_DIR/etc/zope.conf"
if grep -qE '^\s*http-address' "$CONF"; then
  sed -i -E "s#^(\s*http-address\s+)([0-9a-fA-F\.\:\[\]]+:)?([0-9]+)\s*\$#\1\2${HTTP_PORT}#g" "$CONF"
else
  echo "http-address 0.0.0.0:${HTTP_PORT}" >> "$CONF"
fi

# Start
echo "[run] Starting Plone (WSGI) on ${HTTP_PORT}"
exec su -s /bin/bash -c "$INSTANCE_DIR/bin/runwsgi -v $CONF" senaite
