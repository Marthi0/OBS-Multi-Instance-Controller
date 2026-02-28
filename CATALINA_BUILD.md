# macOS Catalina Build Guide

This guide explain how to build and run the OBS Multi Instance Controller on macOS Catalina (10.15).

## Prerequisites

### Hardware
- Mac with Intel processor (x86_64)
- macOS Catalina 10.15 or later

### Software
- Python 3.11 (x86_64 architecture)
- Git
- brew (optional, for package management)

## Installation

### 1. Install Python 3.11 for macOS x86_64

Download from [python.org](https://www.python.org/downloads/):
- Choose "macOS 64-bit universal2" installer (supports both Intel and Apple Silicon correctly)
- Or specifically Intel x86_64 if available

Verify architecture:
```bash
python3 --version
python3 -c "import struct; print(f'Python: {struct.calcsize(\"P\") * 8}-bit')"

# Both should show 64-bit
```

### 2. Clone and Setup Project

```bash
git clone <repo-url>
cd OBS-Multi-Instance-Controller

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
pip install pyinstaller>=6.0.0
```

## Building from Source

### For Catalina x86_64:

```bash
# Clean previous builds
rm -rf build dist

# Build with Catalina compatibility
python scripts/build_macos.py \
  --version 0.1.0 \
  --arch x86_64 \
  --catalina-compat

# App bundle location
open dist/*.app
```

### Environment Variables (Optional)

```bash
# Force Catalina 10.15 deployment target
export MACOSX_DEPLOYMENT_TARGET=10.15

# Then build
python scripts/build_macos.py --version 0.1.0 --arch x86_64 --catalina-compat
```

## Running the Application

### From Source (Development)
```bash
python main.py
```

### From Built App Bundle
```bash
# Find the app bundle
APP_BUNDLE=$(find dist -name "*.app" | head -1)

# Run it
open "$APP_BUNDLE"

# Or directly
"$APP_BUNDLE/Contents/MacOS/obs-multi-instance-controller"
```

## Verification

### Check Python Architecture
```bash
file /usr/local/bin/python3
# Should show: Mach-O 64-bit executable x86_64
```

### Check PySide2 Installation
```bash
python3 -c "import PySide2; print(PySide2.__file__)"
python3 -c "from PySide2.QtWidgets import QApplication; print('✓ PySide2 OK')"
```

### Check Bundle Contents
```bash
APP_BUNDLE=$(find dist -name "*.app" | head -1)

# List bundled libraries
find "$APP_BUNDLE" -name "*.dylib" | head -20

# Check binary dependencies
otool -L "$APP_BUNDLE/Contents/MacOS/obs-multi-instance-controller" | head -20
```

## Troubleshooting

### "unable to load shiboken2"
**Solution:** This error doesn't occur with PySide2 on Catalina. If you see it:
1. Verify Python architecture is 64-bit: `python -c "import struct; print(struct.calcsize('P')*8)"`
2. Reinstall PySide2: `pip install --force-reinstall PySide2>=5.15.0`
3. Rebuild: `rm -rf build dist && python scripts/build_macos.py ...`

### "No matching distribution found for PySide2"
**Solution:** Update pip and setuptools first:
```bash
pip install --upgrade pip setuptools wheel
pip install PySide2>=5.15.0
```

### App won't start from bundle
**Possible issues:**
1. Code signing (Catalina requires it):
   ```bash
   codesign --deep --force --sign - "$APP_BUNDLE"
   ```

2. Architecture mismatch - verify binary:
   ```bash
   file "$APP_BUNDLE/Contents/MacOS/obs-multi-instance-controller"
   # Should show: Mach-O 64-bit executable x86_64
   ```

3. Missing configuration:
   - Ensure `config.json` exists in current directory
   - See `config.template.json` for template

### Performance on Catalina
Qt 5/PySide2 performs identically to Qt 6/PySide6. If you see slowness:
- Check OBS WebSocket connection (network bottleneck)
- Verify CPU/memory usage with Activity Monitor
- Check logs in `logs/` directory for errors

## Building with GitHub Actions

If you want CI/CD builds for x86_64 Catalina compatibility:
1. The repository is already configured for this
2. Push tag: `git tag v0.1.0 && git push origin v0.1.0`
3. GitHub Actions will build automatically for:
   - macOS Intel x86_64 (Catalina compatible)
   - macOS Apple Silicon arm64
   - Windows
   - Linux
4. Find artifacts in Releases page

## Need Help?

See `PYSIDE2_MIGRATION.md` for technical details about the framework choice.
