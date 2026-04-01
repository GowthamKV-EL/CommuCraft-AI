"""Configuration loader for CommuCraft-AI application.

This module handles loading environment variables and user profile configuration.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

from dotenv import load_dotenv


class Config:
    """Configuration manager for CommuCraft-AI.

    Loads and manages environment variables and user profile settings.
    """

    def __init__(self, env_file: str = ".env", profile_file: str = "data/user_profile.json") -> None:
        """
        Initialize configuration by loading .env and user profile.

        Args:
            env_file (str): Path to .env file. Defaults to ".env".
            profile_file (str): Path to user profile JSON file. Defaults to "data/user_profile.json".

        Errors:
            FileNotFoundError: If user_profile.json is not found.
            ValueError: If required environment variables are missing or profile is invalid.
            json.JSONDecodeError: If user_profile.json is invalid JSON.
        """
        # Resolve .env path relative to project root for robustness
        # This ensures the file is found regardless of current working directory
        env_path = Path(__file__).parent.parent.parent / env_file
        load_dotenv(env_path)

        # Get Google API key
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        if not self.google_api_key or self.google_api_key.startswith("your_"):
            raise ValueError(
                "GOOGLE_API_KEY environment variable not set or is a placeholder. "
                "Please update your .env file with a valid Google API key. "
                "See SETUP.md for instructions on obtaining a Google API key."
            )

        # Get daily run time
        self.daily_run_time = os.getenv("DAILY_RUN_TIME", "09:00")
        self._validate_daily_run_time()

        # Load user profile (convert to absolute path relative to project root for robustness)
        # This ensures the file is found regardless of current working directory
        profile_path = (Path(__file__).parent.parent.parent / profile_file).resolve()
        if not profile_path.exists():
            raise FileNotFoundError(
                f"User profile file not found at {profile_path}. "
                "Please run `cp data/user_profile.json.example data/user_profile.json` "
                "and edit with your role and proficiency level. See SETUP.md for details."
            )

        with open(profile_path) as f:
            self.user_profile = json.load(f)

        # Validate user profile
        self._validate_user_profile()

        # Load Confluence configuration (optional)
        self.confluence_url = os.getenv("CONFLUENCE_URL")
        self.confluence_username = os.getenv("CONFLUENCE_USERNAME")
        self.confluence_api_token = os.getenv("CONFLUENCE_API_TOKEN")
        self.confluence_space = os.getenv("CONFLUENCE_SPACE", "COMMUCRAFT")

    def _validate_user_profile(self) -> None:
        """
        Validate that user profile contains required fields.

        Errors:
            ValueError: If required fields are missing from user profile.
        """
        required_fields = ["role", "proficiency_level"]
        for field in required_fields:
            if field not in self.user_profile:
                raise ValueError(f"User profile missing required field: {field}")

    def _validate_daily_run_time(self) -> None:
        """
        Validate that daily_run_time is in correct HH:MM format.

        Errors:
            ValueError: If daily_run_time format is invalid or time values are out of range.
        """
        time_parts = self.daily_run_time.split(":")

        if len(time_parts) < 1 or len(time_parts) > 2:
            raise ValueError(f"DAILY_RUN_TIME must be in HH:MM or HH format, got: {self.daily_run_time}")

        try:
            hour = int(time_parts[0])
            minute = int(time_parts[1]) if len(time_parts) > 1 else 0

            if not (0 <= hour < 24):
                raise ValueError(f"Hour must be 0-23, got: {hour}")

            if not (0 <= minute < 60):
                raise ValueError(f"Minute must be 0-59, got: {minute}")
        except ValueError as e:
            raise ValueError(f"Invalid DAILY_RUN_TIME format '{self.daily_run_time}': {str(e)}")

    @property
    def role(self) -> str:
        """Get user's role from profile."""
        return self.user_profile.get("role", "")

    @property
    def proficiency_level(self) -> str:
        """Get user's proficiency level from profile."""
        return self.user_profile.get("proficiency_level", "")

    @property
    def email(self) -> Optional[str]:
        """Get user's email from profile."""
        return self.user_profile.get("email")

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to dictionary.

        Returns:
            Dict[str, Any]: Dictionary containing all configuration values.
        """
        return {
            "google_api_key": self.google_api_key[:10] + "..." if self.google_api_key else None,
            "daily_run_time": self.daily_run_time,
            "role": self.role,
            "proficiency_level": self.proficiency_level,
            "email": self.email,
        }


def load_config(env_file: str = ".env", profile_file: str = "data/user_profile.json") -> Config:
    """
    Load and return configuration object.

    Args:
        env_file (str): Path to .env file. Defaults to ".env".
        profile_file (str): Path to user profile JSON file. Defaults to "data/user_profile.json".

    Returns:
        Config: Configuration object with all settings loaded.

    Errors:
        FileNotFoundError: If required files are not found.
        ValueError: If required configuration is invalid.
    """
    return Config(env_file=env_file, profile_file=profile_file)
