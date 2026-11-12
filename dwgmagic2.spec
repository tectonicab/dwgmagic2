# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller build: one onedir bundle containing both executables.

dwgmagic2.exe  — console build, used for --cli and for debugging a bad launch.
dwgmagic2w.exe — windowed build, what the shortcut and context menu open.

Onedir rather than onefile: onefile re-extracts to TEMP on every launch, and a
blocked extraction fails the same silent way this rewrite exists to eliminate.
"""
import re
from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files
from PyInstaller.utils.win32.versioninfo import (
    FixedFileInfo,
    StringFileInfo,
    StringStruct,
    StringTable,
    VarFileInfo,
    VarStruct,
    VSVersionInfo,
)

# Read without importing the package (the spec runs in PyInstaller's process).
_VERSION = re.search(
    r'__version__\s*=\s*"([^"]+)"',
    (Path(SPECPATH) / "dwgmagic" / "__init__.py").read_text(encoding="utf-8"),
).group(1)
_VERSION_TUPLE = tuple((list(map(int, _VERSION.split(".")[:4])) + [0, 0, 0, 0])[:4])


def _version_info(original_filename, description):
    """Windows version resource for an executable.

    An unsigned PyInstaller exe with no version resource is what Defender's
    machine-learning model flags (Trojan:Win32/Bearfoos.A!ml quarantined
    dwgmagic2w.exe); identifying the publisher and product lowers that score.
    """

    return VSVersionInfo(
        ffi=FixedFileInfo(
            filevers=_VERSION_TUPLE,
            prodvers=_VERSION_TUPLE,
            mask=0x3F,
            flags=0x0,
            OS=0x40004,  # VOS_NT_WINDOWS32
            fileType=0x1,  # VFT_APP
            subtype=0x0,
            date=(0, 0),
        ),
        kids=[
            StringFileInfo(
                [
                    StringTable(
                        "040904B0",
                        [
                            StringStruct("CompanyName", "Tectonica-B Ltd."),
                            StringStruct("FileDescription", description),
                            StringStruct("FileVersion", _VERSION),
                            StringStruct("InternalName", original_filename.rsplit(".", 1)[0]),
                            StringStruct("LegalCopyright", "Copyright (c) Tectonica-B Ltd."),
                            StringStruct("OriginalFilename", original_filename),
                            StringStruct("ProductName", "DWGMAGIC"),
                            StringStruct("ProductVersion", _VERSION),
                        ],
                    )
                ]
            ),
            VarFileInfo([VarStruct("Translation", [0x0409, 1200])]),
        ],
    )


# build_environment() resolves templates relative to dwgmagic.__file__, so they
# must keep their package-relative location inside the bundle.
datas = [("dwgmagic/templates", "dwgmagic/templates")]
datas += collect_data_files("customtkinter")  # bundled theme JSON + assets
datas += collect_data_files("tkinterdnd2")  # native tkdnd binaries

a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=["tkinterdnd2"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["pytest", "setuptools"],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe_console = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="dwgmagic2",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
    icon="magic.ico",
    version=_version_info("dwgmagic2.exe", "DWGMAGIC (console)"),
)

exe_windowed = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="dwgmagic2w",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    icon="magic.ico",
    version=_version_info("dwgmagic2w.exe", "DWGMAGIC"),
)

coll = COLLECT(
    exe_console,
    exe_windowed,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name="dwgmagic2",
)
