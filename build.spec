# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for School Uniform Billing System.
Build with:  pyinstaller build.spec
"""

import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Collect theme/asset files from customtkinter
ctk_datas = collect_data_files("customtkinter", include_py_files=False)

# Collect reportlab fonts & resources
rl_datas = collect_data_files("reportlab")

a = Analysis(
    ["main.py"],
    pathex=["."],
    binaries=[],
    datas=[
        *ctk_datas,
        *rl_datas,
        ("assets",   "assets"),     # shop logo / extra assets (if any)
    ],
    hiddenimports=[
        # SQLAlchemy
        "sqlalchemy.dialects.sqlite",
        "sqlalchemy.sql.default_comparator",
        # customtkinter
        "customtkinter",
        "darkdetect",
        # win32
        "win32api",
        "win32print",
        "pywintypes",
        # bcrypt
        "bcrypt",
        # reportlab internals
        "reportlab.graphics.barcode",
        "reportlab.graphics.barcode.common",
        "reportlab.graphics.barcode.code128",
        "reportlab.graphics.barcode.code93",
        "reportlab.graphics.barcode.usps",
        "reportlab.graphics.barcode.usps4s",
        "reportlab.graphics.barcode.ecc200datamatrix",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["matplotlib", "numpy", "pandas", "scipy", "IPython"],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="UniformBilling",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,          # no black console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon="assets\\icon.ico" if os.path.exists("assets\\icon.ico") else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="UniformBilling",
)
