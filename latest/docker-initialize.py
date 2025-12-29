import os
from pathlib import Path

HTTP_PORT = os.environ.get("HTTP_PORT", "8080")
ZEO_PORT = os.environ.get("ZEO_PORT", "8100")
PLONE_SITE = os.environ.get("PLONE_SITE", "Plone")

INSTANCE = Path("/home/senaite/senaitelims/parts/instance/etc/zope.conf")
ZEO = Path("/home/senaite/senaitelims/parts/zeoserver/etc/zeo.conf")

def replace(path, key, value):
    txt = path.read_text()
    txt = txt.replace(key, value)
    path.write_text(txt)

if INSTANCE.exists():
    replace(INSTANCE, "http-address 0.0.0.0:8080", f"http-address 0.0.0.0:{HTTP_PORT}")
    replace(INSTANCE, "zeo-address 127.0.0.1:8100", f"zeo-address 127.0.0.1:{ZEO_PORT}")

if ZEO.exists():
    replace(ZEO, "address 8100", f"address {ZEO_PORT}")
