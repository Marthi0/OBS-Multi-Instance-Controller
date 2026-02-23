"""OBS WebSocket connection management."""
import logging
from typing import Optional, Dict, Any
from obsws_python import ReqClient, EventClient
import time

logger = logging.getLogger(__name__)


class WebSocketManager:
    """Manages WebSocket connections to OBS Studio instances."""

    def __init__(self, host: str, port: int, password: str, timeout: float = 5.0):
        """Initialize WebSocket manager.

        Args:
            host: OBS host (usually localhost)
            port: OBS WebSocket port
            password: OBS WebSocket password
            timeout: Connection timeout in seconds
        """
        self.host = host
        self.port = port
        self.password = password
        self.timeout = timeout
        self.req_client: Optional[ReqClient] = None
        self.event_client: Optional[EventClient] = None
        self.connected = False

    def connect(self) -> bool:
        """Establish WebSocket connection to OBS.

        Returns:
            bool: True if connected successfully, False otherwise
        """
        try:
            self.req_client = ReqClient(
                host=self.host,
                port=self.port,
                password=self.password,
                timeout=self.timeout
            )
            self.event_client = EventClient(
                host=self.host,
                port=self.port,
                password=self.password,
                timeout=self.timeout
            )
            self.connected = True
            logger.info(f"Connected to OBS at {self.host}:{self.port}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to OBS at {self.host}:{self.port}: {e}")
            self.connected = False
            return False

    def disconnect(self) -> None:
        """Disconnect from OBS WebSocket."""
        try:
            if self.req_client:
                self.req_client.disconnect()
            if self.event_client:
                self.event_client.disconnect()
            self.connected = False
            logger.info(f"Disconnected from OBS at {self.host}:{self.port}")
        except Exception as e:
            logger.error(f"Error disconnecting from OBS: {e}")
            self.connected = False

    def is_connected(self) -> bool:
        """Check if WebSocket is connected.

        Returns:
            bool: Connection status
        """
        # Quick check: if we don't have a client, we're not connected
        if not self.req_client or not self.connected:
            return False

        # Try a lightweight connection test
        try:
            self.req_client.get_version()
            return True
        except Exception as e:
            # Connection test failed, but only log as debug (not warning)
            # to avoid spam on temporary connection issues
            logger.debug(f"Connection test failed: {e}")
            self.connected = False
            return False

    def start_streaming(self) -> bool:
        """Start streaming on OBS.

        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_connected():
            logger.error("Not connected to OBS")
            return False

        try:
            self.req_client.start_stream()
            logger.info(f"Started streaming on {self.host}:{self.port}")
            return True
        except Exception as e:
            logger.error(f"Failed to start streaming: {e}")
            return False

    def stop_streaming(self) -> bool:
        """Stop streaming on OBS.

        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_connected():
            logger.error("Not connected to OBS")
            return False

        try:
            self.req_client.stop_stream()
            logger.info(f"Stopped streaming on {self.host}:{self.port}")
            return True
        except Exception as e:
            logger.error(f"Failed to stop streaming: {e}")
            return False

    def start_recording(self) -> bool:
        """Start recording on OBS.

        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_connected():
            logger.error("Not connected to OBS")
            return False

        try:
            self.req_client.start_record()
            logger.info(f"Started recording on {self.host}:{self.port}")
            return True
        except Exception as e:
            logger.error(f"Failed to start recording: {e}")
            return False

    def stop_recording(self) -> bool:
        """Stop recording on OBS.

        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_connected():
            logger.error("Not connected to OBS")
            return False

        try:
            self.req_client.stop_record()
            logger.info(f"Stopped recording on {self.host}:{self.port}")
            return True
        except Exception as e:
            logger.error(f"Failed to stop recording: {e}")
            return False

    def get_streaming_status(self) -> bool:
        """Get current streaming status.

        Returns:
            bool: True if streaming, False otherwise
        """
        if not self.is_connected():
            return False

        try:
            response = self.req_client.get_stream_status()
            return response.output_active
        except Exception as e:
            logger.error(f"Failed to get streaming status: {e}")
            return False

    def get_recording_status(self) -> bool:
        """Get current recording status.

        Returns:
            bool: True if recording, False otherwise
        """
        if not self.is_connected():
            return False

        try:
            response = self.req_client.get_record_status()
            return response.output_active
        except Exception as e:
            logger.error(f"Failed to get recording status: {e}")
            return False

    def get_status(self) -> Dict[str, Any]:
        """Get complete OBS status.

        Returns:
            dict: Status information with keys:
                - connected: bool
                - streaming: bool
                - recording: bool
        """
        streaming = self.get_streaming_status()
        recording = self.get_recording_status()

        return {
            "connected": self.is_connected(),
            "streaming": streaming,
            "recording": recording
        }
