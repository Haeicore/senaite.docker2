#!/usr/bin/env python3
import os
import re
import subprocess
from pathlib import Path

ZEO_CONF = Path("/home/senaite/senaitelims/parts/zeoserver/etc/zeo.conf")
ZOPE_CONF = Path("/home/senaite/senaitelims/parts/instance/etc/zope.conf")

DATA_FS = Path("/data/filestorage/Data.fs")
BLOB_DIR = Path("/data/blobstorage")

BIN_INSTANCE = Path("/home/senaite/senaitelims/bin/instance")

def env(name, default=None):
    v = os.environ.get(name)
    return v if (v is not None and v != "") else default

def replace_or_add(conf_path: Path, key_regex: str, new_line: str):
    if not conf_path.exists():
        print(f"[init] WARN: config not found: {conf_path}")
        return
    s = conf_path.read_text(encoding="utf-8", errors="replace").splitlines()
    rx = re.compile(key_regex)
    out = []
    replaced = False
    for line in s:
        if rx.match(line.strip()):
            out.append(new_line)
            replaced = True
        else:
            out.append(line)
    if not replaced:
        out.append(new_line)
    conf_path.write_text("\n".join(out) + "\n", encoding="utf-8")

def run(cmd, check=True):
    print("[init] RUN:", " ".join(cmd))
    return subprocess.run(cmd, check=check)

def ensure_dirs():
    Path("/data/filestorage").mkdir(parents=True, exist_ok=True)
    Path("/data/blobstorage").mkdir(parents=True, exist_ok=True)
    Path("/data/log").mkdir(parents=True, exist_ok=True)
    Path("/data/cache").mkdir(parents=True, exist_ok=True)

def configure_ports():
    http_port = env("HTTP_PORT", "8080")
    zeo_port = env("ZEO_PORT", "8100")
    zeo_bind = env("ZEO_BIND", "0.0.0.0")
    http_bind = env("HTTP_BIND", "0.0.0.0")

    # ZEO conf: address
    # zeo.conf costuma ter "address 0.0.0.0:8100" ou similar
    replace_or_add(
        ZEO_CONF,
        r"^address\s+.*$",
        f"address {zeo_bind}:{zeo_port}",
    )

    # Zope conf: http-address
    replace_or_add(
        ZOPE_CONF,
        r"^http-address\s+.*$",
        f"http-address {http_bind}:{http_port}",
    )

    # Zope conf: zeo-address
    # para host networking, 127.0.0.1 é OK (zeo e web no mesmo host)
    replace_or_add(
        ZOPE_CONF,
        r"^zeo-address\s+.*$",
        f"zeo-address 127.0.0.1:{zeo_port}",
    )

def is_first_run():
    # Se não existe Data.fs, é primeira inicialização
    return not DATA_FS.exists()

def create_site_and_apply_profile():
    site_id = env("PLONE_SITE", "Plone")
    admin_user = env("ADMIN_USER", "admin")
    admin_pass = env("ADMIN_PASSWORD", env("PASSWORD", "admin"))

    # 1) Garante user admin (zope2instance usa adduser via script instance)
    # Isso cria/atualiza o user no emergency user database
    run([str(BIN_INSTANCE), "adduser", admin_user, admin_pass])

    # 2) Cria site Plone (Classic)
    # create-site existe no bin/instance do zope2instance
    run([str(BIN_INSTANCE), "create-site", site_id, "--admin-user", admin_user])

    # 3) Aplica profile do SENAITE (GenericSetup)
    # Roda um snippet via "run" dentro do Zope
    profile = env("PROFILE", "senaite.lims:default")

    script = f"""
from Testing.makerequest import makerequest
from zope.component.hooks import setSite
import transaction

app = makerequest(app)
site = app.get('{site_id}')
setSite(site)

from Products.CMFCore.utils import getToolByName
setup = getToolByName(site, 'portal_setup')
setup.runAllImportStepsFromProfile('profile-{profile}')

transaction.commit()
print("OK: applied profile {profile} on {site_id}")
"""

    run([str(BIN_INSTANCE), "run", "-c", script])

def main():
    print("[init] start docker-initialize.py")
    ensure_dirs()
    configure_ports()

    # Só cria site na primeira vez
    if is_first_run():
        print("[init] First run detected (no Data.fs). Creating site...")
        create_site_and_apply_profile()
    else:
        print("[init] Existing Data.fs found. Skipping site creation.")

if __name__ == "__main__":
    main()
