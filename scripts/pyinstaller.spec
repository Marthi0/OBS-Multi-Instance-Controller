# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec file for OBS Multi Instance Controller across all platforms."""

import sys
import os
from pathlib import Path

block_cipher = None

# Project root
project_root = Path.cwd()

# macOS compatibility settings for Catalina (10.15)
macos_deployment_target = os.environ.get("MACOSX_DEPLOYMENT_TARGET", "10.15")

a = Analysis(
    [str(project_root / "main.py")],
    pathex=[str(project_root)],
    binaries=[],
    datas=[],
    hiddenimports=[
        # PySide6 core modules
        "PySide6.QtCore",
        "PySide6.QtGui",
        "PySide6.QtWidgets",
        "PySide6.QtCore.QCoreApplication",
        "PySide6.QtGui.QGuiApplication",
        "PySide6.QtWidgets.QApplication",
        # PySide6 plugins (required for Catalina)
        "PySide6.plugins.platforms",
        "PySide6.plugins.imageformats",
        "PySide6.plugins.iconengines",
        "PySide6.plugins.platforms.qcocoa",
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
    hookspath=[str(project_root / "scripts")],  # Use custom hooks
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
    upx=False,  # Disable UPX for macOS compatibility with Catalina
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
            "LSMinimumSystemVersion": "10.15.0",  # Catalina minimum
        },
    )
