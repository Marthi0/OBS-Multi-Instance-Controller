"""
PyInstaller hook for PySide6 on macOS Catalina.
Ensures all PySide6 plugins and dependencies are correctly included.
"""

from PyInstaller.utils.hooks import get_module_file_attribute
from pathlib import Path

# Get PySide6 paths
try:
    import PySide6
    pyside6_dir = Path(get_module_file_attribute("PySide6")).parent
except Exception:
    pyside6_dir = None

# Collect all necessary plugins
hiddenimports = [
    "PySide6.QtCore",
    "PySide6.QtGui",
    "PySide6.QtWidgets",
    "PySide6.plugins.platforms.qcocoa",
    "PySide6.plugins.imageformats",
    "PySide6.plugins.iconengines",
]

# Include binary data files from PySide6
datas = []
if pyside6_dir and pyside6_dir.exists():
    # Include plugins directory
    plugins_dir = pyside6_dir / "plugins"
    if plugins_dir.exists():
        datas.append((str(plugins_dir), "PySide6/plugins"))

    # Include Qt libraries
    lib_dir = pyside6_dir / "lib"
    if lib_dir.exists():
        datas.append((str(lib_dir), "PySide6/lib"))

    # Include resources
    resources_dir = pyside6_dir / "resources"
    if resources_dir.exists():
        datas.append((str(resources_dir), "PySide6/resources"))
