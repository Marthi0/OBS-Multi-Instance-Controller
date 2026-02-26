# OBS Multi Instance Controller v0.1.0

**OBS Multi Instance Controller** - Automatically manage and control multiple OBS Studio instances for parallel live streaming.

![Python 3.14+](https://img.shields.io/badge/Python-3.14+-blue)
![PySide6](https://img.shields.io/badge/PySide6-6.8+-green)
![OBS Studio 29.0.2+](https://img.shields.io/badge/OBS_Studio-29.0.2+-orange)

## Overview

OBS Multi Instance Controller is a desktop application that provides centralized control for multiple OBS Studio instances running simultaneously on Windows, macOS or Linux. It's designed for live streaming where you need:

- **Multi-instance OBS management** - Launch and control multiple OBS instances without conflicts
- **Automatic WebSocket configuration** - OBS instances are configured with WebSocket automatically on startup
- **Auto-restart on crash** - Watchdog monitoring with automatic recovery
- **Unified recording/streaming control** - Control all courts from a single interface

## Downloads

Get pre-built binaries for your platform:

| Platform | Download |
|----------|----------|
| **Windows x86-64** | [obs-multi-instance-controller-0.1.0-windows-x86_64.exe](https://github.com/Marthi0/OBS-Multi-Instance-Controller/releases/download/v0.1.0/obs-multi-instance-controller-0.1.0-windows-x86_64.exe) |
| **macOS x86-64** | [obs-multi-instance-controller-0.1.0-macos-x86_64.zip](https://github.com/Marthi0/OBS-Multi-Instance-Controller/releases/download/v0.1.0/obs-multi-instance-controller-0.1.0-macos-x86_64.zip) |
| **macOS ARM64** | [obs-multi-instance-controller-0.1.0-macos-arm64.zip](https://github.com/Marthi0/OBS-Multi-Instance-Controller/releases/download/v0.1.0/obs-multi-instance-controller-0.1.0-macos-arm64.zip) |
| **Linux x86-64** | [obs-multi-instance-controller-0.1.0-linux-x86_64.tar.gz](https://github.com/Marthi0/OBS-Multi-Instance-Controller/releases/download/v0.1.0/obs-multi-instance-controller-0.1.0-linux-x86_64.tar.gz) |

Or [view all releases](https://github.com/Marthi0/OBS-Multi-Instance-Controller/releases).

**Installation:** Simply download the binary for your platform, create a `config.json` file (see Configuration below), and run!

## Features

✨ **v0.1.0 - Initial Release**

- Launch multiple OBS instances with per-instance WebSocket configuration
- Automatic WebSocket parameter setup via CLI (OBS 32.x+)
- Real-time OBS connection monitoring with auto-recovery
- Manual vs. automatic restart detection (no restart on intentional stop)
- Centralized UI for starting/stopping OBS and recording/streaming
- UTF-8 logging with proper character support
- Comprehensive logging with rotation

## Requirements

- **Windows 10+** (tested on Windows)
- **Python 3.14+**
- **OBS Studio 32.0.4+** (for CLI WebSocket configuration)

## Installation

### 1. Clone the repository

```bash
git https://github.com/Marthi0/OBS-Multi-Instance-Controller.git
cd obs-multi-instance-controller
```

### 2. Create virtual environment

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

## Building from Source

To build standalone executables using PyInstaller:

```bash
# Install build dependencies
pip install pyinstaller>=6.0.0

# Build for your platform
python scripts/build_windows.py --version 0.1.0   # Windows
python scripts/build_macos.py --version 0.1.0     # macOS
python scripts/build_linux.py --version 0.1.0     # Linux
```

For detailed build instructions, see [BUILD.md](BUILD.md).

**Automated Builds:** Push a version tag to auto-build for all platforms:
```bash
git tag v0.1.0
git push origin v0.1.0
```

## Configuration

### Create `config.json`

Create a `config.json` file in the project root:

```json
{
  "obs_executable_path": "C:\\Program Files\\obs-studio\\bin\\64bit\\obs64.exe",
  "courts": [
    {
      "name": "Court n°1 Puchaux",
      "obs_port": 4444,
      "websocket_port": 4444,
      "websocket_password": "Puchaux",
      "profile_name": "Puchaux"
    },
    {
      "name": "Court n°2 Bruniera",
      "obs_port": 4445,
      "websocket_port": 4445,
      "websocket_password": "Bruniera",
      "profile_name": "Bruniera"
    }
  ],
  "watchdog_check_interval": 5,
  "watchdog_restart_delay": 3
}
```

### Configuration Details

| Field | Description |
|-------|-------------|
| `obs_executable_path` | Full path to obs64.exe or obs32.exe |
| `courts` | Array of court configurations |
| `name` | Display name for the court (supports Unicode) |
| `obs_port` | Unused in v0.1.0, for future compatibility |
| `websocket_port` | Port for OBS WebSocket server |
| `websocket_password` | Password for WebSocket authentication |
| `profile_name` | OBS profile name to use |
| `watchdog_check_interval` | Seconds between health checks (default: 5) |
| `watchdog_restart_delay` | Seconds to wait before attempting recovery (default: 3) |

## Usage

### Launch the application

```bash
python main.py
```

### Application Flow

1. **Application starts** → Watchdogs are created and started
2. **Click "Start OBS"** → OBS process launches with WebSocket configured
3. **Connection established** → UI shows green indicator and enables control buttons
4. **Record/Stream controls** → Use buttons to control OBS recording and streaming
5. **Click "Stop OBS"** → Stops the OBS process (watchdog will NOT auto-restart)
6. **OBS crashes** → Watchdog automatically restarts OBS and reconnects

### WebSocket Configuration

OBS is automatically launched with:

```
obs64.exe --profile <profile_name> --multi --websocket_port <port> --websocket_password <password>
```

- `--multi`: Allows multiple OBS instances on Windows
- `--websocket_port`: Configures WebSocket port
- `--websocket_password`: Sets WebSocket password

## Project Structure

```
obs-multi-instance-controller/
├── app/
│   ├── config/           # Configuration loading and models
│   ├── obs/              # OBS WebSocket communication
│   ├── system/           # Process management and watchdog
│   ├── ui/               # Qt-based user interface
│   └── utils/            # Logging and utilities
├── logs/                 # Application logs (auto-created)
├── tests/                # Unit tests
├── config.json           # Configuration file (user-created)
├── main.py              # Application entry point
├── requirements.txt     # Python dependencies
└── pyproject.toml      # Project metadata
```

### Key Components

**OBS Launcher** (`app/system/obs_launcher.py`)
- Launches OBS processes with proper CLI configuration
- Manages process lifecycle (start, stop, restart)
- Logs command line for debugging

**Watchdog** (`app/system/watchdog.py`)
- Monitors OBS connection health every 5 seconds
- Distinguishes between manual stops and crashes
- Automatically restarts failed OBS instances
- Includes exponential backoff for recovery attempts

**WebSocket Manager** (`app/obs/websocket_manager.py`)
- Handles WebSocket connection to OBS
- Manages recording/streaming state
- Provides thread-safe connection interface

**UI** (`app/ui/`)
- PySide6-based Qt interface
- Real-time status indicator
- Per-court control panels
- Status and error messaging

## Logging

Logs are written to `logs/app.log` with:

- UTF-8 encoding for proper character support
- Automatic rotation (10MB per file, keeps 5 backups)
- Timestamp, logger name, level, and message

Example log entries:

```
[2026-02-23 14:45:57] [app.system.obs_launcher] [INFO] Launching OBS with command: C:\Program Files\obs-studio\bin\64bit\obs64.exe --profile Puchaux --multi --websocket_port 4444 --websocket_password Puchaux
[2026-02-23 14:45:59] [app.system.obs_launcher] [INFO] Launched OBS for profile Puchaux (PID: 185592)
[2026-02-23 14:46:02] [app.obs.websocket_manager] [INFO] Connected to OBS at localhost:4444
```

## Troubleshooting

### OBS doesn't start

1. **Check OBS executable path** in `config.json`
2. **Verify OBS is installed**: `C:\Program Files\obs-studio\bin\64bit\obs64.exe`
3. **Check logs**: `logs/app.log` for detailed error messages
4. **Verify profiles exist**: `%APPDATA%\obs-studio\profiles\<profile_name>\`

### Connection refused errors

1. **Check ports are available**:
   ```bash
   netstat -ano | findstr :4444
   netstat -ano | findstr :4445
   ```

2. **Kill conflicting processes** if needed

3. **Check WebSocket is enabled in OBS**: Settings → General → Make connections to obs-websocket server

### UTF-8 encoding issues in logs

- Application automatically handles UTF-8 encoding
- Ensure `config.json` is saved as UTF-8
- Logs are written with UTF-8 encoding

## Testing

```bash
# Run all tests
pytest tests/

# Run specific test
pytest tests/test_watchdog.py -v
```

## Development

### Code Style

Uses black formatting and isort for imports:

```bash
pip install black isort
black app/
isort app/
```

### Adding Features

1. Create feature branch: `git checkout -b feature/my-feature`
2. Implement and test
3. Commit with descriptive message
4. Push and create pull request

## Known Limitations

- **Windows only** - Currently designed for Windows; Linux/macOS support planned
- **Single machine** - Controls OBS on local machine only; remote OBS planned
- **Basic monitoring** - Watchdog does simple connection tests; advanced diagnostics planned

## Future Roadmap

### v1.0.0
- [ ] Linux support
- [ ] macOS support
- [ ] startup scene selection
- [ ] youtube stream monitoring
- [ ] match starts and ending to cut records
- [ ] automatic record upload
- [ ] disk space monitoring

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - See LICENSE file for details

## Support

For issues, questions, or suggestions:

- **GitHub Issues**: Report bugs and request features
- **Discussions**: General questions and discussions

## Credits

Built with:

- [PySide6](https://www.qt.io/qt-for-python) - Qt framework for Python
- [obsws-python](https://github.com/Chatzi/obsws_python) - OBS WebSocket library
- [Pydantic](https://docs.pydantic.dev/) - Data validation

## Changelog

### v0.1.0 (Initial Release) - February 23, 2026

- Multi-instance OBS launching and management
- Automatic WebSocket configuration via CLI
- OBS connection monitoring with watchdog
- Auto-restart on crash (manual stop detection)
- UTF-8 logging with proper encoding
- Basic recording/streaming controls
- Real-time connection status indicator

---

**OBS Multi Instance Controller v0.1.0** - Making multi instance streaming simple and reliable.
