# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec file for OBS Multi Instance Controller across all platforms."""

import sys
from pathlib import Path

block_cipher = None

# Project root
project_root = Path.cwd()

a = Analysis(
    [str(project_root / "main.py")],
    pathex=[str(project_root)],
    binaries=[],
    datas=[],
    hiddenimports=[
        # PySide6 core
        "PySide6.QtCore",
        "PySide6.QtGui",
        "PySide6.QtWidgets",
        # PySide6 platform plugins and resources
        "PySide6.QtCore.QCoreApplication",
        "PySide6.QtGui.QGuiApplication",
        # obsws-python
        "obsws_python",
        "obsws_python.client",
        # Pydantic
        "pydantic",
        "pydantic.json",
        # psutil
        "psutil",
        # Standard library
        "logging",
        "logging.handlers",
        "json",
        "pathlib",
        "threading",
        "time",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludedimports=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="obs-multi-instance-controller",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # GUI application, no console window
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# For macOS: Create app bundle
if sys.platform == "darwin":
    app = BUNDLE(
        exe,
        name="OBS Multi Instance Controller.app",
        icon=None,
        bundle_identifier=None,
        info_plist={
            "NSPrincipalClass": "NSApplication",
            "NSHighResolutionCapable": "True",
            "NSRequiresIPhoneOS": False,
        },
    )
