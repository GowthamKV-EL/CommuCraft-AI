"""
Configuration management for CommuCraft-AI application.

This module handles environment variables and application settings using Pydantic
for validation and type safety.

Args:
    None

Returns:
    None

Errors:
    ValueError: If required environment variables are missing or invalid.
"""

from pathlib import Path

from pydantic import Field, ValidationError, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Google API Configuration
    google_api_key: str = Field(..., description="Google Gemini API key")

    # Daily Learning Configuration
    daily_learning_time: str = Field(default="09:00", description="Time to run daily learning task (HH:MM format)")
    user_proficiency_level: str = Field(
        default="intermediate", description="User's English proficiency level (beginner/intermediate/advanced)"
    )
    user_role_focus: str = Field(default="general", description="User's role or domain focus for learning")

    # Text-to-Speech Configuration
    tts_language_code: str = Field(default="en-US", description="Language code for text-to-speech")
    tts_voice_name: str = Field(default="en-US-Neural2-A", description="Voice name for text-to-speech")

    # Storage Configuration
    data_dir: str = Field(default="./data", description="Directory for storing data files")
    storage_type: str = Field(default="json", description="Type of storage (json/sqlite)")

    # Application Configuration
    log_level: str = Field(default="INFO", description="Logging level")
    debug: bool = Field(default=False, description="Debug mode")

    class Config:
        """Pydantic configuration for Settings."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    @field_validator("daily_learning_time")
    @classmethod
    def validate_time_format(cls, v: str) -> str:
        """
        Validate that daily_learning_time is in HH:MM format.

        Args:
            v (str): The time string to validate.

        Returns:
            str: The validated time string.

        Errors:
            ValueError: If time format is invalid.
        """
        try:
            parts = v.split(":")
            if len(parts) != 2:
                raise ValueError
            hour = int(parts[0])
            minute = int(parts[1])
            if not (0 <= hour < 24 and 0 <= minute < 60):
                raise ValueError
        except (ValueError, IndexError) as e:
            raise ValueError(f"Time must be in HH:MM format (24-hour), got {v}") from e
        return v

    @field_validator("user_proficiency_level")
    @classmethod
    def validate_proficiency_level(cls, v: str) -> str:
        """
        Validate that user_proficiency_level is one of the allowed values.

        Args:
            v (str): The proficiency level to validate.

        Returns:
            str: The validated proficiency level.

        Errors:
            ValueError: If proficiency level is not valid.
        """
        allowed = ["beginner", "intermediate", "advanced"]
        if v.lower() not in allowed:
            raise ValueError(f"Proficiency level must be one of {allowed}, got {v}")
        return v.lower()

    @field_validator("storage_type")
    @classmethod
    def validate_storage_type(cls, v: str) -> str:
        """
        Validate that storage_type is one of the allowed values.

        Args:
            v (str): The storage type to validate.

        Returns:
            str: The validated storage type.

        Errors:
            ValueError: If storage type is not valid.
        """
        allowed = ["json", "sqlite"]
        if v.lower() not in allowed:
            raise ValueError(f"Storage type must be one of {allowed}, got {v}")
        return v.lower()

    def get_data_dir(self) -> Path:
        """
        Get the data directory path, creating it if it doesn't exist.

        Args:
            None

        Returns:
            Path: The data directory path.

        Errors:
            OSError: If directory cannot be created.
        """
        data_path = Path(self.data_dir)
        data_path.mkdir(parents=True, exist_ok=True)
        return data_path


def load_settings() -> Settings:
    """
    Load and validate application settings from environment.

    Args:
        None

    Returns:
        Settings: Validated settings object.

    Errors:
        ValidationError: If settings validation fails.
    """
    try:
        return Settings()
    except ValidationError as e:
        raise ValidationError(f"Failed to load settings: {e}") from e


# Global settings instance
settings = load_settings()
