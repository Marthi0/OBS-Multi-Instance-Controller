# Building OBS Multi Instance Controller

This document describes how to build OBS Multi Instance Controller binaries for different platforms using PyInstaller.

## Quick Start

### Using GitHub Actions (Recommended)

The easiest way to get pre-built binaries is:

1. Create a version tag: `git tag v0.1.0`
2. Push the tag: `git push origin v0.1.0`
3. GitHub Actions automatically builds for all platforms
4. Download binaries from [GitHub Releases](https://github.com/Marthi0/OBS-Multi-Instance-Controller/releases)

### Local Build

To build locally on your platform:

```bash
# Install build dependencies
pip install pyinstaller>=6.0.0

# Build
python build/build_windows.py --version 0.1.0 --output dist/   # Windows
python build/build_macos.py --version 0.1.0 --output dist/     # macOS
python build/build_linux.py --version 0.1.0 --output dist/     # Linux
```

## Detailed Setup

### Prerequisites

#### All Platforms

```bash
# Clone the repository
git clone https://github.com/Marthi0/OBS-Multi-Instance-Controller
cd obs-multi-instance-controller

# Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate      # Windows

# Install dependencies
pip install -r requirements.txt
pip install pyinstaller
```

#### Windows-Specific

- Python 3.11+ installed
- No additional requirements

#### macOS-Specific

- Python 3.11+ installed (recommend from python.org or Homebrew)
- Xcode Command Line Tools: `xcode-select --install`

#### Linux-Specific

- Python 3.11+ and development headers
- Qt5 development libraries

```bash
# Ubuntu/Debian
sudo apt-get install python3-dev python3-pyside6 libqt6core6

# Fedora/RHEL
sudo dnf install python3-devel qt6-qtbase-devel
```

## Build Scripts

### Windows Build

```bash
python build/build_windows.py --version 0.1.0 --output dist/
```

**Output:** `dist/obs-multi-instance-controller-0.1.0-windows-x86_64.exe`

**Features:**
- Single executable file
- No console window
- Bundled with all dependencies
- Size: ~400-500 MB

**Testing:**
```bash
dist/obs-multi-instance-controller-0.1.0-windows-x86_64.exe
```

### macOS Build

```bash
python build/build_macos.py --version 0.1.0 --output dist/
```

**Output:** `dist/obs-multi-instance-controller-0.1.0-macos-{x86_64|arm64}.zip`

**Features:**
- Builds for current architecture (x86_64 or ARM64)
- Creates app bundle (.app)
- Distributed as ZIP archive
- Size: ~400-500 MB

**Testing:**
```bash
# Extract
unzip dist/obs-multi-instance-controller-0.1.0-macos-arm64.zip

# Run
open OBS\ Multi\ Instance\ Controller.app

# Or run directly
./OBS\ Multi\ Instance\ Controller.app/Contents/MacOS/obs-multi-instance-controller
```

**macOS Security Note:**
On first run, you may see:
> "OBS Multi Instance Controller.app" cannot be opened because the developer cannot be verified.

This is expected for unsigned builds. Click "Open" anyway or allow in Security settings.

### Linux Build

```bash
python build/build_linux.py --version 0.1.0 --output dist/
```

**Output:** `dist/obs-multi-instance-controller-0.1.0-linux-x86_64.tar.gz`

**Features:**
- Single executable
- Bundled dependencies
- Distributed as TAR.GZ archive
- Size: ~400-500 MB

**Testing:**
```bash
# Extract
tar xzf dist/obs-multi-instance-controller-0.1.0-linux-x86_64.tar.gz

# Run
./dist/obs-multi-instance-controller
```

## GitHub Actions Workflow

The workflow (`.github/workflows/build-and-release.yml`) automatically:

1. **Triggers on:**
   - Version tags: `git tag v*.*.*`
   - Manual workflow dispatch

2. **Builds for:**
   - Windows x86-64 (windows-latest)
   - macOS x86-64 (macos-latest)
   - macOS ARM64 (runs on ARM64 runner)
   - Linux x86-64 (ubuntu-latest)

3. **Creates:**
   - GitHub Release with all binaries
   - Artifacts available for 30 days

4. **Release Assets:**
   ```
   obs-multi-instance-controller-0.1.0-windows-x86_64.exe
   obs-multi-instance-controller-0.1.0-macos-x86_64.zip
   obs-multi-instance-controller-0.1.0-macos-arm64.zip
   obs-multi-instance-controller-0.1.0-linux-x86_64.tar.gz
   ```

## Manual Release Process

To manually trigger a release build:

1. Go to: **Actions** → **Build and Release** → **Run workflow**
2. Enter version: `0.1.0`
3. Click "Run workflow"
4. Artifacts available under workflow run
5. Create release manually if needed:
   ```bash
   gh release create v0.1.0 dist/obs-multi-instance-controller-* --generate-notes
   ```

## Troubleshooting

### PyInstaller Issues

**Error: "PyInstaller not found"**
```bash
pip install pyinstaller
```

**Error: "Failed to find PySide6 dependencies"**
- Ensure PySide6 is installed: `pip install PySide6`
- On Linux, may need Qt libraries: `apt-get install python3-pyside6`

### Build Size

Binaries are large (~400-500 MB) due to:
- PySide6 GUI framework
- Qt libraries
- Python runtime

This is normal. Compression during release reduces transferred size.

### Platform Issues

**Windows: Missing msvcrt or DLL errors**
- Ensure Visual C++ Redistributable is installed
- Building on Windows handles this automatically

**macOS: Code signature verification**
- Unsigned builds show security warnings
- This is expected; users can open anyway
- For production, add code signing and notarization

**Linux: Missing dependencies**
- Ensure all development headers installed
- PySide6 should be pre-installed in bundle
- May need to add `libqt6core6` or similar

### Git Tag Issues

**Error: "Invalid version format"**
```bash
# Ensure tag format is v*.*.*
git tag v0.1.0
git push origin v0.1.0
```

**Error: "Failed to get git tag"**
```bash
# Verify git is available
git --version

# For manual builds, specify version explicitly
python build/build_windows.py --version 0.1.0
```

## Configuration File

**Important:** The built binary does NOT include `config.json`. Users must provide it.

Location depends on where binary is run from:
```
./config.json              ← Checked first (same directory as binary)
~/config.json              ← Checked second (home directory)
```

**For users:**
1. Download binary
2. Create `config.json` in same directory as binary
3. Run binary

**Example config.json:**
```json
{
  "obs_executable_path": "C:\\Program Files\\obs-studio\\bin\\64bit\\obs64.exe",
  "courts": [
    {
      "name": "Court n°1",
      "obs_port": 4444,
      "websocket_port": 4444,
      "websocket_password": "password",
      "profile_name": "profile_name"
    }
  ],
  "watchdog_check_interval": 5,
  "watchdog_restart_delay": 3
}
```

## Advanced: Custom Builds

### Modify PyInstaller Options

Edit `build/pyinstaller.spec`:
```python
# Add hidden imports
hiddenimports=[
    # ... existing imports
    "your_custom_module",
],

# Change icon (Windows/macOS)
exe = EXE(
    # ...
    icon="path/to/icon.ico",  # Windows
    # ...
)

# For macOS app bundle
app = BUNDLE(
    exe,
    name="Custom Name.app",
    # ...
)
```

### Custom Version String

```bash
python build/build_windows.py --version my-custom-version
```

### Output Customization

Modify `build/build.py` `get_artifact_name()` to change naming scheme.

## Version Management

Versions are extracted from git tags in format `v*.*.*`:
- `v0.1.0` → `0.1.0`
- `v1.2.3` → `1.2.3`
- Invalid formats cause build errors

## CI/CD Integration

The GitHub Actions workflow can be extended:

```yaml
# Publish to PyPI
- uses: pypa/gh-action-pypi-publish@release/v1

# Publish to S3
- uses: jakejarvis/s3-sync-action@master

# Create Chocolatey package (Windows)
- run: choco pack obs-multi-instance-controller.nuspec

# Create APT/RPM packages (Linux)
- run: fpm -s dir -t deb -n obs-multi-instance-controller ...
```

## Next Steps

1. **Test build locally:** `python build/build_windows.py --version 0.1.0`
2. **Create version tag:** `git tag v0.1.0`
3. **Push tag:** `git push origin v0.1.0`
4. **Monitor workflow:** Check GitHub Actions tab
5. **Download binaries:** From GitHub Releases
6. **Distribute:** Share release link with users

---

For issues, see [Troubleshooting](#troubleshooting) or create a GitHub issue.
