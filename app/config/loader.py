"""Configuration loader."""
import json
from pathlib import Path
from typing import Optional
from pydantic import ValidationError
from .models import AppConfig
import logging

logger = logging.getLogger(__name__)


class ConfigLoader:
    """Load and validate application configuration from JSON file."""

    def __init__(self, config_path: str = "config.json"):
        """Initialize config loader.

        Args:
            config_path: Path to config.json file
        """
        self.config_path = Path(config_path)

    def load(self) -> AppConfig:
        """Load and validate configuration.

        Returns:
            AppConfig: Validated configuration object

        Raises:
            FileNotFoundError: If config file doesn't exist
            json.JSONDecodeError: If JSON is invalid
            ValidationError: If configuration is invalid
        """
        if not self.config_path.exists():
            raise FileNotFoundError(
                f"Configuration file not found: {self.config_path.absolute()}"
            )

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                config_data = json.load(f)
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(
                f"Invalid JSON in config file: {e.msg}",
                e.doc,
                e.pos
            )

        try:
            config = AppConfig(**config_data)
        except ValidationError as e:
            logger.error(f"Configuration validation error: {e}")
            raise

        # Validate OBS executable path exists
        obs_path = Path(config.obs_executable_path)
        if not obs_path.exists():
            raise FileNotFoundError(
                f"OBS executable not found: {obs_path.absolute()}"
            )

        logger.info(f"Configuration loaded successfully from {self.config_path}")
        return config
