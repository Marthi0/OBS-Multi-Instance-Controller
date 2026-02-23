# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-02-23

### Added

- **Multi-instance OBS launching** - Launch multiple OBS instances simultaneously on Windows
- **Automatic WebSocket configuration** - OBS instances are configured with WebSocket parameters automatically via CLI flags (--websocket_port, --websocket_password)
- **OBS connection monitoring** - Watchdog continuously checks OBS health and automatically restarts failed instances
- **Manual vs automatic restart detection** - Distinguishes between user-initiated stops (no auto-restart) and crashes (auto-restart)
- **Centralized UI control** - Single application to control recording/streaming on multiple courts
- **Real-time connection status** - Visual indicator showing connection status (green/red)
- **Per-court control panels** - Independent controls for each court instance
- **UTF-8 logging support** - Proper encoding for accented characters and special symbols (e.g., n°1)
- **Automatic log rotation** - Logs rotate at 10MB with 5 backups kept
- **Configuration via JSON** - Simple config.json for setup
- **Error messaging** - User-friendly error notifications in UI
- **Command-line logging** - Full OBS launch command logged for debugging

### Technical

- Built with PySide6 for Qt framework
- Uses obsws-python for OBS WebSocket communication
- Pydantic for configuration validation
- Thread-safe watchdog monitoring
- Proper resource cleanup on shutdown

### Known Limitations

- **Windows only** - Currently Windows-only; Linux/macOS planned
- **Local only** - Controls OBS on the same machine; remote support planned
- **Basic monitoring** - Simple connection checking; advanced diagnostics planned
- **No remote streaming setup** - Manual configuration required for streaming parameters

## [Unreleased]

### Planned for v1.0.0

- Linux support
- macOS support
- startup scene selection
- youtube stream monitoring
- match starts and ending to cut records
- automatic record upload
- disk space monitoring
