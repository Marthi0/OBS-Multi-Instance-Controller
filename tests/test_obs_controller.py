"""Tests for OBS controller."""
import pytest
from unittest.mock import Mock, MagicMock, patch
from app.obs.controller import OBSController
from app.config.models import CourtConfig


class TestOBSController:
    """Test OBSController."""

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
    def controller(self, court_config):
        """Create an OBS controller instance."""
        return OBSController(court_config)

    def test_controller_initialization(self, controller, court_config):
        """Test controller initialization."""
        assert controller.court_config == court_config
        assert controller.ws_manager is not None

    def test_connect(self, controller):
        """Test connect method."""
        with patch.object(controller.ws_manager, 'connect', return_value=True):
            result = controller.connect()
            assert result is True

    def test_disconnect(self, controller):
        """Test disconnect method."""
        with patch.object(controller.ws_manager, 'disconnect') as mock_disconnect:
            controller.disconnect()
            mock_disconnect.assert_called_once()

    def test_is_connected(self, controller):
        """Test is_connected method."""
        with patch.object(controller.ws_manager, 'is_connected', return_value=True):
            result = controller.is_connected()
            assert result is True

    def test_start_streaming(self, controller):
        """Test start_streaming method."""
        with patch.object(controller.ws_manager, 'start_streaming', return_value=True):
            result = controller.start_streaming()
            assert result is True

    def test_stop_streaming(self, controller):
        """Test stop_streaming method."""
        with patch.object(controller.ws_manager, 'stop_streaming', return_value=True):
            result = controller.stop_streaming()
            assert result is True

    def test_start_recording(self, controller):
        """Test start_recording method."""
        with patch.object(controller.ws_manager, 'start_recording', return_value=True):
            result = controller.start_recording()
            assert result is True

    def test_stop_recording(self, controller):
        """Test stop_recording method."""
        with patch.object(controller.ws_manager, 'stop_recording', return_value=True):
            result = controller.stop_recording()
            assert result is True

    def test_get_status(self, controller):
        """Test get_status method."""
        expected_status = {
            "connected": True,
            "streaming": False,
            "recording": True
        }
        with patch.object(controller.ws_manager, 'get_status', return_value=expected_status):
            result = controller.get_status()
            assert result == expected_status
