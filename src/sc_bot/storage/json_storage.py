"""
JSON-based storage system for CommuCraft-AI.

This module provides persistent storage functionality for daily learning content,
user profiles, and communication history using JSON files.

Args:
    None

Returns:
    None

Errors:
    IOError: If file operations fail.
    json.JSONDecodeError: If JSON parsing fails.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from sc_bot.config import settings

logger = logging.getLogger(__name__)


class JSONStorage:
    """
    JSON-based storage system for persistent data.

    This class manages reading and writing JSON files for storing daily learning
    content, user profiles, and communication history.

    Args:
        data_dir (Path | None): Directory to store JSON files. Uses settings if None.

    Returns:
        None

    Errors:
        IOError: If directory creation fails.
    """

    def __init__(self, data_dir: Optional[Path] = None) -> None:
        """
        Initialize JSON storage with data directory.

        Args:
            data_dir (Path | None): Directory to store JSON files. Defaults to None.

        Returns:
            None

        Errors:
            IOError: If directory cannot be created.
        """
        self.data_dir = data_dir or settings.get_data_dir()
        self.data_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"JSONStorage initialized at {self.data_dir}")

    def save_daily_learning(self, content: dict[str, Any]) -> None:
        """
        Save daily learning content with timestamp.

        Args:
            content (dict[str, Any]): Daily learning content including paragraph and vocabulary.

        Returns:
            None

        Errors:
            IOError: If file write fails.
            json.JSONDecodeError: If JSON serialization fails.

        Example:
            Input: {"paragraph": "...", "words": [...], "proficiency": "intermediate"}
            Output: None (writes to daily_learning_YYYY-MM-DD.json)
        """
        date_str = datetime.now().strftime("%Y-%m-%d")
        file_path = self.data_dir / f"daily_learning_{date_str}.json"

        try:
            data = {"timestamp": datetime.now().isoformat(), "content": content}
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"Daily learning saved to {file_path}")
        except (IOError, json.JSONDecodeError) as e:
            logger.error(f"Failed to save daily learning: {e}")
            raise

    def load_daily_learning(self, date_str: Optional[str] = None) -> Optional[dict[str, Any]]:
        """
        Load daily learning content for a specific date.

        Args:
            date_str (str | None): Date in YYYY-MM-DD format. Uses today if None.

        Returns:
            dict[str, Any] | None: Daily learning content or None if not found.

        Errors:
            IOError: If file read fails.
            json.JSONDecodeError: If JSON parsing fails.

        Example:
            Input: "2024-03-23"
            Output: {"timestamp": "...", "content": {"paragraph": "...", "words": [...]}}
        """
        if date_str is None:
            date_str = datetime.now().strftime("%Y-%m-%d")

        file_path = self.data_dir / f"daily_learning_{date_str}.json"

        try:
            if not file_path.exists():
                logger.info(f"Daily learning file not found: {file_path}")
                return None

            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            logger.info(f"Daily learning loaded from {file_path}")
            return data
        except (IOError, json.JSONDecodeError) as e:
            logger.error(f"Failed to load daily learning: {e}")
            return None

    def save_user_profile(self, user_id: str, profile: dict[str, Any]) -> None:
        """
        Save or update user profile.

        Args:
            user_id (str): Unique user identifier.
            profile (dict[str, Any]): User profile data including proficiency level and preferences.

        Returns:
            None

        Errors:
            IOError: If file write fails.
            json.JSONDecodeError: If JSON serialization fails.

        Example:
            Input: user_id="user123", profile={"proficiency": "intermediate", "role": "manager"}
            Output: None (writes to user_profiles.json)
        """
        file_path = self.data_dir / "user_profiles.json"

        try:
            profiles = {}
            if file_path.exists():
                with open(file_path, "r", encoding="utf-8") as f:
                    profiles = json.load(f)

            profiles[user_id] = {"last_updated": datetime.now().isoformat(), **profile}

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(profiles, f, indent=2, ensure_ascii=False)
            logger.info(f"User profile saved for {user_id}")
        except (IOError, json.JSONDecodeError) as e:
            logger.error(f"Failed to save user profile: {e}")
            raise

    def load_user_profile(self, user_id: str) -> Optional[dict[str, Any]]:
        """
        Load user profile by ID.

        Args:
            user_id (str): Unique user identifier.

        Returns:
            dict[str, Any] | None: User profile data or None if not found.

        Errors:
            IOError: If file read fails.
            json.JSONDecodeError: If JSON parsing fails.

        Example:
            Input: "user123"
            Output: {"last_updated": "...", "proficiency": "intermediate", "role": "manager"}
        """
        file_path = self.data_dir / "user_profiles.json"

        try:
            if not file_path.exists():
                logger.info("User profiles file not found")
                return None

            with open(file_path, "r", encoding="utf-8") as f:
                profiles = json.load(f)

            profile = profiles.get(user_id)
            if profile:
                logger.info(f"User profile loaded for {user_id}")
            return profile
        except (IOError, json.JSONDecodeError) as e:
            logger.error(f"Failed to load user profile: {e}")
            return None

    def save_communication_history(self, user_id: str, entry: dict[str, Any]) -> None:
        """
        Save communication rewriting history entry.

        Args:
            user_id (str): Unique user identifier.
            entry (dict[str, Any]): Communication entry with original and rewritten messages.

        Returns:
            None

        Errors:
            IOError: If file write fails.
            json.JSONDecodeError: If JSON serialization fails.

        Example:
            Input: user_id="user123", entry={"type": "email", "original": "...", "rewritten": "..."}
            Output: None (appends to communication_history_user123.json)
        """
        file_path = self.data_dir / f"communication_history_{user_id}.json"

        try:
            history = []
            if file_path.exists():
                with open(file_path, "r", encoding="utf-8") as f:
                    history = json.load(f)

            entry_with_timestamp = {"timestamp": datetime.now().isoformat(), **entry}
            history.append(entry_with_timestamp)

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
            logger.info(f"Communication history saved for {user_id}")
        except (IOError, json.JSONDecodeError) as e:
            logger.error(f"Failed to save communication history: {e}")
            raise

    def load_communication_history(self, user_id: str, limit: Optional[int] = None) -> list[dict[str, Any]]:
        """
        Load communication history for a user.

        Args:
            user_id (str): Unique user identifier.
            limit (int | None): Maximum number of recent entries to load. None for all.

        Returns:
            list[dict[str, Any]]: List of communication history entries.

        Errors:
            IOError: If file read fails.
            json.JSONDecodeError: If JSON parsing fails.

        Example:
            Input: user_id="user123", limit=10
            Output: [{"timestamp": "...", "type": "email", "original": "...", "rewritten": "..."}]
        """
        file_path = self.data_dir / f"communication_history_{user_id}.json"

        try:
            if not file_path.exists():
                logger.info(f"Communication history file not found for {user_id}")
                return []

            with open(file_path, "r", encoding="utf-8") as f:
                history = json.load(f)

            if limit:
                history = history[-limit:]
            logger.info(f"Communication history loaded for {user_id} ({len(history)} entries)")
            return history
        except (IOError, json.JSONDecodeError) as e:
            logger.error(f"Failed to load communication history: {e}")
            return []

    def save_meeting_prep(self, user_id: str, prep_data: dict[str, Any]) -> None:
        """
        Save meeting preparation content.

        Args:
            user_id (str): Unique user identifier.
            prep_data (dict[str, Any]): Meeting preparation data including talking points and concerns.

        Returns:
            None

        Errors:
            IOError: If file write fails.
            json.JSONDecodeError: If JSON serialization fails.

        Example:
            Input: user_id="user123", prep_data={"meeting_id": "m1", "talking_points": [...]}
            Output: None (writes to meeting_prep_user123.json)
        """
        file_path = self.data_dir / f"meeting_prep_{user_id}.json"

        try:
            preps = []
            if file_path.exists():
                with open(file_path, "r", encoding="utf-8") as f:
                    preps = json.load(f)

            prep_with_timestamp = {"timestamp": datetime.now().isoformat(), **prep_data}
            preps.append(prep_with_timestamp)

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(preps, f, indent=2, ensure_ascii=False)
            logger.info(f"Meeting preparation saved for {user_id}")
        except (IOError, json.JSONDecodeError) as e:
            logger.error(f"Failed to save meeting preparation: {e}")
            raise

    def list_files(self, pattern: Optional[str] = None) -> list[Path]:
        """
        List all stored files, optionally filtered by pattern.

        Args:
            pattern (str | None): Glob pattern to filter files. None for all files.

        Returns:
            list[Path]: List of file paths.

        Errors:
            None

        Example:
            Input: "daily_learning_*.json"
            Output: [Path("daily_learning_2024-03-23.json"), Path("daily_learning_2024-03-22.json")]
        """
        if pattern is None:
            return sorted(self.data_dir.glob("*.json"))
        return sorted(self.data_dir.glob(pattern))
