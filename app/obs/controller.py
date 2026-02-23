"""High-level OBS controller."""
import logging
from typing import Dict, Any
from .websocket_manager import WebSocketManager
from app.config.models import CourtConfig

logger = logging.getLogger(__name__)


class OBSController:
    """High-level OBS control abstraction."""

    def __init__(self, court_config: CourtConfig):
        """Initialize OBS controller for a court.

        Args:
            court_config: CourtConfig object with court settings
        """
        self.court_config = court_config
        self.ws_manager = WebSocketManager(
            host="localhost",
            port=court_config.websocket_port,
            password=court_config.websocket_password
        )

    def connect(self) -> bool:
        """Connect to OBS WebSocket."""
        return self.ws_manager.connect()

    def disconnect(self) -> None:
        """Disconnect from OBS."""
        self.ws_manager.disconnect()

    def is_connected(self) -> bool:
        """Check if connected to OBS."""
        return self.ws_manager.is_connected()

    def start_streaming(self) -> bool:
        """Start streaming."""
        return self.ws_manager.start_streaming()

    def stop_streaming(self) -> bool:
        """Stop streaming."""
        return self.ws_manager.stop_streaming()

    def start_recording(self) -> bool:
        """Start recording."""
        return self.ws_manager.start_recording()

    def stop_recording(self) -> bool:
        """Stop recording."""
        return self.ws_manager.stop_recording()

    def get_streaming_status(self) -> bool:
        """Get streaming status."""
        return self.ws_manager.get_streaming_status()

    def get_recording_status(self) -> bool:
        """Get recording status."""
        return self.ws_manager.get_recording_status()

    def get_status(self) -> Dict[str, Any]:
        """Get complete status."""
        return self.ws_manager.get_status()
