"""OBS watchdog monitoring and auto-restart."""
import logging
import threading
import time
from typing import Callable, Optional
from app.obs.controller import OBSController
from app.system.obs_launcher import OBSLauncher
from app.config.models import CourtConfig

logger = logging.getLogger(__name__)


class OBSWatchdog:
    """Monitor OBS health and auto-restart on failure."""

    def __init__(
        self,
        court_config: CourtConfig,
        obs_launcher: OBSLauncher,
        obs_controller: OBSController,
        check_interval: int = 5,
        restart_delay: int = 3,
        on_disconnect: Optional[Callable] = None,
        on_reconnect: Optional[Callable] = None
    ):
        """Initialize watchdog.

        Args:
            court_config: Court configuration
            obs_launcher: OBS launcher instance
            obs_controller: OBS controller instance
            check_interval: Seconds between health checks
            restart_delay: Seconds to wait before restarting
            on_disconnect: Callback when disconnected
            on_reconnect: Callback when reconnected
        """
        self.court_config = court_config
        self.obs_launcher = obs_launcher
        self.obs_controller = obs_controller
        self.check_interval = check_interval
        self.restart_delay = restart_delay
        self.on_disconnect = on_disconnect
        self.on_reconnect = on_reconnect

        self.thread: Optional[threading.Thread] = None
        self.running = False
        self.was_connected = False
        self.manually_stopped = False  # Track if user manually stopped OBS

    def start(self) -> None:
        """Start watchdog monitoring."""
        if self.running:
            logger.warning(f"Watchdog already running for {self.court_config.name}")
            return

        # Initialize the connection state before starting monitoring
        self.was_connected = self.obs_controller.is_connected()

        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
        logger.info(f"Watchdog started for {self.court_config.name}")

    def stop(self) -> None:
        """Stop watchdog monitoring."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info(f"Watchdog stopped for {self.court_config.name}")

    def _monitor_loop(self) -> None:
        """Main watchdog monitoring loop."""
        # Wait a bit before starting to check (let OBS fully initialize)
        time.sleep(self.check_interval)

        while self.running:
            try:
                self._health_check()
            except Exception as e:
                logger.error(f"Watchdog error for {self.court_config.name}: {e}")

            time.sleep(self.check_interval)

    def _health_check(self) -> None:
        """Perform health check and take action if needed."""
        is_connected = self.obs_controller.is_connected()

        # Connection state changed
        if is_connected != self.was_connected:
            self.was_connected = is_connected

            if not is_connected:
                logger.warning(f"OBS disconnected for {self.court_config.name}")
                if self.on_disconnect:
                    self.on_disconnect()

                # Only attempt recovery if not manually stopped
                if not self.manually_stopped:
                    self._attempt_recovery()
                else:
                    logger.info(f"OBS was manually stopped for {self.court_config.name}, not attempting recovery")
            else:
                logger.info(f"OBS reconnected for {self.court_config.name}")
                self.manually_stopped = False  # Reset flag on reconnect
                if self.on_reconnect:
                    self.on_reconnect()

    def mark_as_manually_stopped(self) -> None:
        """Mark OBS as manually stopped by user (prevent auto-restart)."""
        self.manually_stopped = True
        logger.info(f"OBS for {self.court_config.name} marked as manually stopped")

    def _attempt_recovery(self) -> None:
        """Attempt to recover from disconnection."""
        logger.info(f"Attempting recovery for {self.court_config.name}")

        time.sleep(self.restart_delay)

        # First try to reconnect to existing process
        if self.obs_controller.connect():
            logger.info(f"Reconnected to existing OBS for {self.court_config.name}")
            return

        # If reconnect fails, restart OBS
        logger.info(f"Restarting OBS for {self.court_config.name}")
        if self.obs_launcher.restart():
            # Wait for OBS to initialize WebSocket
            logger.info(f"Waiting for OBS to reinitialize WebSocket for {self.court_config.name}...")
            time.sleep(5)

            # Try to connect again
            if self.obs_controller.connect():
                logger.info(f"Successfully restarted OBS for {self.court_config.name}")
                return

        logger.error(f"Failed to recover OBS for {self.court_config.name}")
