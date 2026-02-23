# Development Guide

## Setting Up Development Environment

### 1. Clone and setup

```bash
git clone https://github.com/yourusername/sco-live.git
cd sco-live
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install -e ".[dev]"
```

### 2. Install development tools

```bash
pip install black isort pytest pytest-cov
```

## Project Structure

```
app/
├── __init__.py
├── __version__.py           # Version information
├── config/
│   ├── loader.py           # JSON configuration loader
│   ├── models.py           # Pydantic models
│   └── obs_config.py       # OBS configuration (reference)
├── obs/
│   ├── controller.py       # OBS control interface
│   └── websocket_manager.py # WebSocket communication
├── system/
│   ├── obs_launcher.py     # Process launching
│   └── watchdog.py         # Health monitoring
├── ui/
│   ├── main_window.py      # Main application window
│   ├── styles/             # Qt stylesheets
│   └── widgets/
│       └── court_control_widget.py  # Per-court UI panel
└── utils/
    └── logging.py          # Logging configuration

main.py                      # Entry point
requirements.txt             # Dependencies
pyproject.toml              # Project metadata
README.md                    # User documentation
CHANGELOG.md                # Version history
```

## Code Standards

### Style

Use black for formatting:

```bash
black app/ main.py
```

### Imports

Use isort for import organization:

```bash
isort app/ main.py
```

### Type Hints

All functions should have type hints:

```python
def launch(self) -> bool:
    """Launch OBS process.

    Returns:
        bool: True if launched successfully, False otherwise
    """
```

### Docstrings

Use Google-style docstrings:

```python
def method(self, param1: str, param2: int) -> str:
    """Short description.

    Longer description if needed.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        str: Description of return value

    Raises:
        ValueError: When something is wrong
    """
```

## Testing

### Run tests

```bash
pytest tests/
pytest tests/test_watchdog.py -v
```

### Coverage

```bash
pytest --cov=app --cov-report=html
```

## Debugging

### Enable verbose logging

Set log level in `app/utils/logging.py`:

```python
setup_logging(log_dir="logs", log_level=logging.DEBUG)
```

### Inspect OBS WebSocket

Use obsws-python directly:

```python
from obsws_python import ReqClient
import asyncio

async def test():
    client = ReqClient(host='localhost', port=4444, password='Puchaux')
    info = await client.call('GetVersion')
    print(info)

asyncio.run(test())
```

## Common Tasks

### Add a new configuration parameter

1. Update `app/config/models.py` (Pydantic model)
2. Update `config.json` template in README.md
3. Add logging in loader if needed
4. Update WEBSOCKET_SETUP.md if relevant

### Add a new UI button

1. Add to `CourtControlWidget._setup_ui()` in `app/ui/widgets/court_control_widget.py`
2. Connect button signal: `self.button.clicked.connect(self._on_button_clicked)`
3. Implement handler: `def _on_button_clicked(self) -> None:`
4. Emit appropriate signal: `self.signal.emit(message)`

### Handle OBS state changes

1. Monitor in `OBSWatchdog._health_check()`
2. Update UI via signals in `CourtControlWidget`
3. Log state changes in appropriate logger

### Add logging

```python
import logging
logger = logging.getLogger(__name__)

logger.info("Information message")
logger.warning("Warning - check this")
logger.error("Error occurred", exc_info=True)
```

## Release Process

### For v0.2.0+

1. **Update version**:
   - Edit `app/__version__.py`
   - Update `pyproject.toml`

2. **Update documentation**:
   - Update `CHANGELOG.md` with changes
   - Update `README.md` if needed

3. **Run tests**:
   ```bash
   pytest tests/
   ```

4. **Tag release**:
   ```bash
   git tag v0.2.0
   git push origin v0.2.0
   ```

## Architecture Notes

### Watchdog Pattern

The watchdog monitors OBS health with these states:

- **Connected**: OBS responsive and ready
- **Disconnected**: Connection lost, attempting recovery
- **Recovery**: Trying to restart OBS
- **Manually Stopped**: User initiated stop, skip auto-restart

### Thread Safety

- Watchdog runs in daemon thread
- UI updates via Qt signals/slots (thread-safe)
- WebSocket messages are serialized
- No direct thread synchronization needed (signals handle it)

### Error Handling

- Exceptions caught in watchdog loop
- Failed launches logged with full details
- Connection errors handled gracefully
- UI shows user-friendly error messages

## Performance Considerations

- Watchdog checks every 5 seconds (configurable)
- WebSocket timeout: 5 seconds
- OBS startup wait: 2-3 seconds
- UI updates: 2 seconds (status timer)

## Future Improvements

- [ ] Linux support
- [ ] macOS support
- [ ] startup scene selection
- [ ] youtube stream monitoring
- [ ] match starts and ending to cut records
- [ ] automatic record upload
- [ ] disk space monitoring
