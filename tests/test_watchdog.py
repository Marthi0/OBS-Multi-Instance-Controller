"""Tests for OBS watchdog monitoring."""
import pytest
import time
from unittest.mock import Mock, MagicMock, patch
from app.system.watchdog import OBSWatchdog
from app.config.models import CourtConfig
from app.obs.controller import OBSController
from app.system.obs_launcher import OBSLauncher


class TestOBSWatchdog:
    """Test OBSWatchdog."""

    @pytest.fixture
    def court_config(self):
        """Create a test court configuration."""
        return CourtConfig(
            name="Test Court",
            obs_port=4444,
            websocket_port=4444,
            websocket_password="test_password",
            profile_name="test_profile"
        )

    @pytest.fixture
    def mock_controller(self):
        """Create a mock OBS controller."""
        controller = Mock(spec=OBSController)
        controller.is_connected.return_value = True
        return controller

    @pytest.fixture
    def mock_launcher(self):
        """Create a mock OBS launcher."""
        launcher = Mock(spec=OBSLauncher)
        launcher.restart.return_value = True
        launcher.is_running.return_value = True
        return launcher

    @pytest.fixture
    def watchdog(self, court_config, mock_launcher, mock_controller):
        """Create an OBS watchdog instance."""
        return OBSWatchdog(
            court_config=court_config,
            obs_launcher=mock_launcher,
            obs_controller=mock_controller,
            check_interval=1,
            restart_delay=1
        )

    def test_watchdog_initialization(self, watchdog):
        """Test watchdog initialization."""
        assert watchdog.running is False
        assert watchdog.was_connected is False

    def test_watchdog_start(self, watchdog):
        """Test watchdog start."""
        watchdog.start()
        assert watchdog.running is True
        assert watchdog.thread is not None
        watchdog.stop()

    def test_watchdog_stop(self, watchdog):
        """Test watchdog stop."""
        watchdog.start()
        assert watchdog.running is True
        watchdog.stop()
        assert watchdog.running is False

    def test_watchdog_disconnect_callback(self, watchdog, mock_controller):
        """Test watchdog calls disconnect callback."""
        disconnect_called = False

        def on_disconnect():
            nonlocal disconnect_called
            disconnect_called = True

        watchdog.on_disconnect = on_disconnect
        watchdog.was_connected = True
        mock_controller.is_connected.return_value = False

        # Check disconnect
        watchdog._health_check()
        # Wait for any async operations
        time.sleep(0.1)
        assert disconnect_called is True

    def test_watchdog_reconnect_callback(self, watchdog, mock_controller):
        """Test watchdog calls reconnect callback."""
        reconnect_called = False

        def on_reconnect():
            nonlocal reconnect_called
            reconnect_called = True

        watchdog.on_reconnect = on_reconnect
        watchdog.was_connected = False
        watchdog.manually_stopped = False

        # Simulate reconnection
        mock_controller.is_connected.return_value = True
        watchdog._health_check()

        assert reconnect_called is True
        assert watchdog.was_connected is True

    def test_watchdog_recovery_attempt(self, watchdog, mock_launcher, mock_controller):
        """Test watchdog recovery attempt."""
        watchdog.was_connected = True
        watchdog.manually_stopped = False
        mock_controller.is_connected.return_value = False

        # First check: disconnect
        watchdog._health_check()

        # Assert that disconnect was triggered
        assert watchdog.was_connected is False

    def test_watchdog_manually_stopped_flag(self, watchdog, mock_controller):
        """Test watchdog respects manually_stopped flag."""
        watchdog.was_connected = True
        watchdog.manually_stopped = True
        mock_controller.is_connected.return_value = False

        # Even though disconnected, shouldn't attempt recovery
        watchdog._health_check()

        # Should NOT attempt to reconnect
        mock_controller.connect.assert_not_called()

    def test_watchdog_mark_as_manually_stopped(self, watchdog):
        """Test marking OBS as manually stopped."""
        assert watchdog.manually_stopped is False

        watchdog.mark_as_manually_stopped()

        assert watchdog.manually_stopped is True

    def test_watchdog_reset_manually_stopped_on_reconnect(self, watchdog, mock_controller):
        """Test manually_stopped flag is reset on reconnect."""
        watchdog.was_connected = False
        watchdog.manually_stopped = True
        mock_controller.is_connected.return_value = True

        watchdog._health_check()

        assert watchdog.manually_stopped is False
        assert watchdog.was_connected is True
