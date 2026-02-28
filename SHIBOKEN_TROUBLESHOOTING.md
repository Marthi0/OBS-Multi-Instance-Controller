# Shiboken Loading Error - Troubleshooting Guide

## Error
```
unable to load shiboken
```

This error occurs when PyInstaller fails to properly bundle PySide6's Shiboken library, which is the C++ binding layer for Qt.

## Solutions

### 1. **Verify Python Architecture Matches System**

On macOS x86_64, you must use x86_64 Python:

```bash
python -c "import struct; print(f'Python: {struct.calcsize(\"P\") * 8}-bit')"
uname -m
```

Both should show `x86_64`. If not:
- Download universal2 or x86_64-specific Python from python.org
- Install matching architecture Python

### 2. **Force Reinstall PySide6 Wheels**

```bash
# Remove cached wheels
pip cache purge

# Force reinstall matching your architecture
pip install --no-cache-dir --force-reinstall PySide6>=6.8.0

# Verify installation
python -c "import PySide6; print(PySide6.__file__)"
python -c "from PySide6.shiboken6 import shiboken6; print('✓ Shiboken OK')"
```

### 3. **Test PyInstaller Locally**

```bash
# Clean previous builds
rm -rf build dist

# Build with diagnostics
python scripts/build_macos.py --version 0.1.0 --arch x86_64 --catalina-compat

# Check the bundle
APP_BUNDLE=$(find dist -name "*.app" | head -1)
otool -L "$APP_BUNDLE/Contents/MacOS/obs-multi-instance-controller" | grep -i shiboken
```

### 4. **Check Bundle Contents**

```bash
APP_BUNDLE=$(find dist -name "*.app" | head -1)

# Should show Shiboken library
find "$APP_BUNDLE" -name "*shiboken*" -o -name "*libQt*"

# Check for broken dylib references
find "$APP_BUNDLE" -type f -name "*.dylib" | while read lib; do
  echo "Checking: $lib"
  otool -D "$lib" | head -1
done
```

### 5. **Run App Bundle Directly**

```bash
APP_BUNDLE=$(find dist -name "*.app" | head -1)
"$APP_BUNDLE/Contents/MacOS/obs-multi-instance-controller"
```

If you see missing library errors, check the output of:
```bash
otool -L "$APP_BUNDLE/Contents/MacOS/obs-multi-instance-controller"
```

### 6. **Environment Variables for Debug**

```bash
# Enable verbose PyInstaller output
python scripts/build_macos.py \
  --version 0.1.0 \
  --arch x86_64 \
  --catalina-compat \
  2>&1 | tee build.log

# Check for Shiboken in build output
grep -i shiboken build.log
```

### 7. **macOS Catalina Specific Issues**

Catalina (10.15) requires:
- Code signing (even for local testing):
  ```bash
  codesign --deep --force --verify --verbose --sign - "$APP_BUNDLE"
  ```

- Ensure binary compatibility:
  ```bash
  otool -L "$APP_BUNDLE/Contents/MacOS/obs-multi-instance-controller" | grep "10.15\|10.14" || echo "May have compatibility issue"
  ```

### 8. **Last Resort: Use GitHub Actions**

The CI pipeline includes diagnostic steps that will show:
- Python and system architecture
- PySide6 installation location
- Shiboken availability
- Bundle contents verification

Check the workflow logs on GitHub Actions for the build that fails.

## Prevention Checklist

- [ ] Python version matches system (x86_64 for Intel Macs)
- [ ] `MACOSX_DEPLOYMENT_TARGET=10.15` is set
- [ ] PySide6 version >= 6.8.0
- [ ] PyInstaller version >= 6.0.0
- [ ] Clean build: `rm -rf build dist`
- [ ] Fresh dependencies: `pip install --force-reinstall PySide6>=6.8.0`

## Still Having Issues?

1. Check GitHub Actions logs for diagnostic output
2. Run build locally with verbose output
3. Compare Python executable architecture with system
4. Verify PySide6 wheels match your Python architecture
