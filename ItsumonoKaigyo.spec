# -*- mode: python ; coding: utf-8 -*-

from datetime import datetime, timedelta, timezone
from pathlib import Path
import re


def update_build_version():
    now = datetime.now(timezone(timedelta(hours=9)))
    version = now.strftime("%Y%m%d-%H%M%S")
    build_datetime = now.strftime("%Y-%m-%d %H:%M:%S +09:00")
    source_path = Path("itsumono_kaigyo.py")
    source = source_path.read_text(encoding="utf-8")
    source = re.sub(r'APP_VERSION = "[^"]+"', f'APP_VERSION = "{version}"', source, count=1)
    source = re.sub(
        r'APP_BUILD_DATETIME = "[^"]+"',
        f'APP_BUILD_DATETIME = "{build_datetime}"',
        source,
        count=1,
    )
    source_path.write_text(source, encoding="utf-8")


update_build_version()

a = Analysis(
    ["itsumono_kaigyo.py"],
    pathex=[],
    binaries=[],
    datas=[("app_icon.ico", ".")],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="ItsumonoKaigyoForChat",
    icon="app_icon.ico",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
