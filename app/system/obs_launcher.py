"""OBS process launching and management."""
import logging
import subprocess
import platform
from pathlib import Path
from typing import Optional
import time

logger = logging.getLogger(__name__)


class OBSLauncher:
    """Launch and manage OBS Studio processes."""

    def __init__(self, obs_executable: str, profile: str, websocket_port: int, websocket_password: str):
        """Initialize OBS launcher.

        Args:
            obs_executable: Path to OBS executable
            profile: OBS profile name to use
            websocket_port: WebSocket server port
            websocket_password: WebSocket server password
        """
        self.obs_executable = Path(obs_executable)
        self.profile = profile
        self.websocket_port = websocket_port
        self.websocket_password = websocket_password
        self.process: Optional[subprocess.Popen] = None
        self.system = platform.system()

    def launch(self) -> bool:
        """Launch OBS process.

        Returns:
            bool: True if launched successfully, False otherwise
        """
        if self.is_running():
            logger.warning(f"OBS is already running for profile {self.profile}")
            return True

        if not self.obs_executable.exists():
            logger.error(f"OBS executable not found: {self.obs_executable}")
            return False

        try:
            # Build command with websocket configuration
            cmd = self._build_command()
            logger.info(f"Launching OBS with command: {' '.join(cmd)}")

            # Launch from OBS directory to ensure all resources are found
            obs_dir = self.obs_executable.parent

            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=(self.system != "Windows"),
                cwd=str(obs_dir)
            )

            # Give OBS time to start
            time.sleep(2)

            if self.is_running():
                logger.info(f"Launched OBS for profile {self.profile} (PID: {self.process.pid})")
                logger.info(f"  WebSocket configured: port={self.websocket_port}")
                return True
            else:
                logger.error(f"OBS process failed to start for profile {self.profile}")
                return False

        except Exception as e:
            logger.error(f"Failed to launch OBS: {e}")
            return False

    def _build_command(self) -> list:
        """Build OBS launch command with appropriate flags.

        Returns:
            list: Command and arguments for subprocess
        """
        cmd = [str(self.obs_executable)]

        # Add profile flag
        cmd.extend(["--profile", self.profile])

        # Multi-instance mode for Windows
        if self.system == "Windows":
            cmd.append("--multi")

        # Configure WebSocket via command-line (OBS 32.x+)
        cmd.extend(["--websocket_port", str(self.websocket_port)])
        cmd.extend(["--websocket_password", self.websocket_password])

        return cmd

    def is_running(self) -> bool:
        """Check if OBS process is running.

        Returns:
            bool: True if process is running, False otherwise
        """
        if self.process is None:
            return False

        return self.process.poll() is None

    def stop(self, timeout: int = 10) -> bool:
        """Stop the OBS process gracefully.

        Args:
            timeout: Seconds to wait before force killing

        Returns:
            bool: True if stopped successfully, False otherwise
        """
        if self.process is None or not self.is_running():
            return True

        try:
            # Graceful shutdown
            if self.system == "Windows":
                self.process.terminate()
            else:
                self.process.terminate()

            # Wait for process to exit
            try:
                self.process.wait(timeout=timeout)
                logger.info(f"OBS stopped for profile {self.profile}")
                return True
            except subprocess.TimeoutExpired:
                logger.warning(f"OBS did not stop gracefully, killing process")
                self.process.kill()
                self.process.wait()
                logger.info(f"OBS killed for profile {self.profile}")
                return True

        except Exception as e:
            logger.error(f"Error stopping OBS: {e}")
            return False

    def restart(self) -> bool:
        """Restart the OBS process.

        Returns:
            bool: True if restarted successfully, False otherwise
        """
        logger.info(f"Restarting OBS for profile {self.profile}")
        self.stop()
        time.sleep(1)
        return self.launch()
