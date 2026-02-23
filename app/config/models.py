"""Configuration data models."""
from typing import List
from pydantic import BaseModel, Field, field_validator
import re


class CourtConfig(BaseModel):
    """Configuration for a single court."""
    name: str = Field(..., description="Court name (e.g., 'Court 1')")
    obs_port: int = Field(..., description="OBS application port")
    websocket_port: int = Field(..., description="OBS WebSocket port")
    websocket_password: str = Field(..., description="OBS WebSocket password")
    profile_name: str = Field(..., description="OBS profile name")

    @field_validator("obs_port", "websocket_port")
    @classmethod
    def validate_port(cls, v: int) -> int:
        """Validate port is in valid range."""
        if not (1 <= v <= 65535):
            raise ValueError("Port must be between 1 and 65535")
        return v

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Ensure name is not empty."""
        if not v.strip():
            raise ValueError("Name cannot be empty")
        return v.strip()


class AppConfig(BaseModel):
    """Application configuration."""
    obs_executable_path: str = Field(
        ...,
        description="Path to OBS executable"
    )
    courts: List[CourtConfig] = Field(
        ...,
        min_length=1,
        description="List of court configurations"
    )
    watchdog_check_interval: int = Field(
        default=5,
        description="Seconds between watchdog health checks"
    )
    watchdog_restart_delay: int = Field(
        default=3,
        description="Seconds to wait before restarting OBS"
    )

    @field_validator("obs_executable_path")
    @classmethod
    def validate_path(cls, v: str) -> str:
        """Ensure path is not empty."""
        if not v.strip():
            raise ValueError("OBS executable path cannot be empty")
        return v.strip()

    @field_validator("watchdog_check_interval", "watchdog_restart_delay")
    @classmethod
    def validate_interval(cls, v: int) -> int:
        """Ensure intervals are positive."""
        if v <= 0:
            raise ValueError("Interval must be positive")
        return v
