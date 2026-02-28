# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec file for OBS Multi Instance Controller - PyQt5/Qt5 Edition."""

import sys
import os
from pathlib import Path

block_cipher = None

# Project root
project_root = Path.cwd()

# macOS compatibility settings
# For Catalina and later support, set minimum deployment target
macos_deployment_target = os.environ.get("MACOSX_DEPLOYMENT_TARGET", "10.13")

a = Analysis(
    [str(project_root / "main.py")],
    pathex=[str(project_root)],
    binaries=[],
    datas=[],
    hiddenimports=[
        # PyQt5 core modules (Qt 5)
        "PyQt5.QtCore",
        "PyQt5.QtGui",
        "PyQt5.QtWidgets",
        # PyQt5 platform plugins (required for GUI)
        "PyQt5.plugins.platforms",
        "PyQt5.plugins.imageformats",
        "PyQt5.plugins.iconengines",
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
        # Encoding support
        "encodings.utf_8",
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
    upx=False,
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
        bundle_identifier="com.obscontroller.multiinstance",
        info_plist={
            "NSPrincipalClass": "NSApplication",
            "NSHighResolutionCapable": "True",
            "NSRequiresIPhoneOS": False,
            "LSMinimumSystemVersion": "10.13.0",  # High Sierra minimum for PyQt5
        },
    )


