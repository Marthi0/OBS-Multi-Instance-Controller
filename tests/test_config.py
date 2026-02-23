"""Tests for configuration loading and validation."""
import pytest
from pathlib import Path
from pydantic import ValidationError
from app.config.models import CourtConfig, AppConfig
from app.config.loader import ConfigLoader
import json
import tempfile


class TestCourtConfig:
    """Test CourtConfig model."""

    def test_valid_court_config(self):
        """Test creating a valid court configuration."""
        config = CourtConfig(
            name="Court 1",
            obs_port=4444,
            websocket_port=4444,
            websocket_password="password123",
            profile_name="court_1"
        )
        assert config.name == "Court 1"
        assert config.obs_port == 4444
        assert config.websocket_port == 4444

    def test_invalid_port_range(self):
        """Test validation of port numbers."""
        with pytest.raises(ValidationError):
            CourtConfig(
                name="Court 1",
                obs_port=99999,  # Invalid port
                websocket_port=4444,
                websocket_password="password123",
                profile_name="court_1"
            )

    def test_empty_name(self):
        """Test validation of empty court name."""
        with pytest.raises(ValidationError):
            CourtConfig(
                name="",  # Empty name
                obs_port=4444,
                websocket_port=4444,
                websocket_password="password123",
                profile_name="court_1"
            )

    def test_name_whitespace_trimmed(self):
        """Test that name whitespace is trimmed."""
        config = CourtConfig(
            name="  Court 1  ",
            obs_port=4444,
            websocket_port=4444,
            websocket_password="password123",
            profile_name="court_1"
        )
        assert config.name == "Court 1"


class TestAppConfig:
    """Test AppConfig model."""

    def test_valid_app_config(self):
        """Test creating valid app configuration."""
        config = AppConfig(
            obs_executable_path="/path/to/obs",
            courts=[
                CourtConfig(
                    name="Court 1",
                    obs_port=4444,
                    websocket_port=4444,
                    websocket_password="password123",
                    profile_name="court_1"
                )
            ]
        )
        assert config.obs_executable_path == "/path/to/obs"
        assert len(config.courts) == 1

    def test_invalid_interval(self):
        """Test validation of watchdog intervals."""
        with pytest.raises(ValidationError):
            AppConfig(
                obs_executable_path="/path/to/obs",
                courts=[],
                watchdog_check_interval=0  # Invalid: must be positive
            )

    def test_empty_courts_list(self):
        """Test validation of courts list."""
        with pytest.raises(ValidationError):
            AppConfig(
                obs_executable_path="/path/to/obs",
                courts=[]  # Invalid: must have at least one court
            )


class TestConfigLoader:
    """Test ConfigLoader."""

    def test_load_valid_config(self):
        """Test loading a valid configuration file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            config_data = {
                "obs_executable_path": __file__,  # Use a real file that exists
                "courts": [
                    {
                        "name": "Court 1",
                        "obs_port": 4444,
                        "websocket_port": 4444,
                        "websocket_password": "password123",
                        "profile_name": "court_1"
                    }
                ]
            }
            json.dump(config_data, f)
            f.flush()

            loader = ConfigLoader(f.name)
            config = loader.load()

            assert len(config.courts) == 1
            assert config.courts[0].name == "Court 1"

    def test_load_nonexistent_file(self):
        """Test loading a nonexistent configuration file."""
        loader = ConfigLoader("nonexistent_file.json")
        with pytest.raises(FileNotFoundError):
            loader.load()

    def test_load_invalid_json(self):
        """Test loading invalid JSON."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("{invalid json")
            f.flush()

            loader = ConfigLoader(f.name)
            with pytest.raises(json.JSONDecodeError):
                loader.load()
