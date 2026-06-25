# -*- mode: python ; coding: utf-8 -*-

from datetime import datetime, timedelta, timezone
from pathlib import Path
import os
import re
import tempfile


def update_build_version():
    now = datetime.now(timezone(timedelta(hours=9)))
    version = now.strftime("%Y%m%d-%H%M%S")
    build_datetime = now.strftime("%Y-%m-%d %H:%M:%S +09:00")
    source_path = Path("itsumono_kaigyo.py")

    # Read as raw bytes and decode without newline translation so the
    # file's original CRLF line endings are preserved exactly.
    original_bytes = source_path.read_bytes()
    source = original_bytes.decode("utf-8")

    updated, count_version = re.subn(
        r'APP_VERSION = "[^"]+"', f'APP_VERSION = "{version}"', source, count=1
    )
    updated, count_datetime = re.subn(
        r'APP_BUILD_DATETIME = "[^"]+"',
        f'APP_BUILD_DATETIME = "{build_datetime}"',
        updated,
        count=1,
    )

    # Safety guard: if either marker is missing, do not touch the file.
    # This prevents an unexpected regex mismatch from rewriting the source.
    if count_version != 1 or count_datetime != 1:
        print(
            "update_build_version: version markers not found "
            f"(APP_VERSION={count_version}, APP_BUILD_DATETIME={count_datetime}); "
            "skipping source rewrite."
        )
        return

    new_bytes = updated.encode("utf-8")
    if new_bytes == original_bytes:
        return

    # Write atomically: write to a temp file in the same directory, then
    # os.replace() it over the original. os.replace is atomic on Windows
    # and POSIX, so a crash mid-write can never leave a truncated source.
    directory = source_path.resolve().parent
    fd, tmp_name = tempfile.mkstemp(dir=str(directory), suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as tmp_file:
            tmp_file.write(new_bytes)
            tmp_file.flush()
            os.fsync(tmp_file.fileno())
        os.replace(tmp_name, str(source_path))
    except BaseException:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise


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
