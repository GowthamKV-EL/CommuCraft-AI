"""JSON storage for daily learning content.

This module handles saving and loading daily learning content to/from JSON files.
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional

from commucraft_ai.utils.logger import get_logger

logger = get_logger("daily_storage")


class DailyContentValidator:
    """Validates daily content structure."""

    REQUIRED_FIELDS = ["date", "role", "proficiency_level", "intro_message", "paragraph", "vocabulary"]
    WORD_REQUIRED_FIELDS = ["word", "meaning", "usage_example", "pronunciation"]

    @staticmethod
    def validate(content: Dict[str, Any]) -> bool:
        """
        Validate that content has all required fields with correct structure.

        Args:
            content (Dict[str, Any]): Content dictionary to validate.

        Returns:
            bool: True if valid, raises ValueError otherwise.

        Errors:
            ValueError: If required fields are missing or have incorrect structure.
        """
        # Check top-level required fields
        for field in DailyContentValidator.REQUIRED_FIELDS:
            if field not in content:
                raise ValueError(f"Missing required field: {field}")

        # Validate intro_message is non-empty string
        if not isinstance(content["intro_message"], str) or not content["intro_message"].strip():
            raise ValueError("Intro message must be a non-empty string")

        # Validate paragraph is non-empty string
        if not isinstance(content["paragraph"], str) or not content["paragraph"].strip():
            raise ValueError("Paragraph must be a non-empty string")

        # Validate vocabulary
        if not isinstance(content["vocabulary"], list):
            raise ValueError("Vocabulary must be a list")

        if len(content["vocabulary"]) < 10 or len(content["vocabulary"]) > 20:
            raise ValueError("Vocabulary must contain 10-20 words")

        # Validate each word
        for idx, word_entry in enumerate(content["vocabulary"]):
            for field in DailyContentValidator.WORD_REQUIRED_FIELDS:
                if field not in word_entry:
                    raise ValueError(f"Word {idx} missing required field: {field}")

                if not isinstance(word_entry[field], str) or not word_entry[field].strip():
                    raise ValueError(f"Word {idx} field '{field}' must be non-empty string")

        return True


def save_daily_content(content: Dict[str, Any], output_dir: str = "data/daily_content") -> Path:
    """
    Save daily learning content to JSON file.

    Creates the output directory if it doesn't exist. Validates content before saving.
    Overwrites existing content for the same date (regenerate on demand).

    Args:
        content (Dict[str, Any]): Daily content dictionary with all fields.
        output_dir (str): Directory to save JSON files. Defaults to "data/daily_content".

    Returns:
        Path: Path to the saved JSON file.

    Errors:
        ValueError: If content fails validation.
        OSError: If directory cannot be created or file cannot be written.
    """
    # Validate content
    DailyContentValidator.validate(content)

    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Create filename from date
    date = content["date"]
    file_path = output_path / f"{date}.json"

    # Write to file
    try:
        with open(file_path, "w") as f:
            json.dump(content, f, indent=2)
        logger.info(f"Saved daily content to {file_path}")
        return file_path
    except OSError as e:
        logger.error(f"Failed to save daily content: {str(e)}")
        raise


def load_daily_content(date: str, content_dir: str = "data/daily_content") -> Optional[Dict[str, Any]]:
    """
    Load daily learning content from JSON file.

    Args:
        date (str): Date in YYYY-MM-DD format.
        content_dir (str): Directory containing JSON files. Defaults to "data/daily_content".

    Returns:
        Dict[str, Any]: Content dictionary if file exists, None otherwise.

    Errors:
        json.JSONDecodeError: If JSON file is malformed.
    """
    file_path = Path(content_dir) / f"{date}.json"

    if not file_path.exists():
        logger.debug(f"No content found for date {date}")
        return None

    try:
        with open(file_path) as f:
            content = json.load(f)
        logger.info(f"Loaded daily content from {file_path}")
        return content
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON file {file_path}: {str(e)}")
        raise


def get_latest_content(content_dir: str = "data/daily_content") -> Optional[Dict[str, Any]]:
    """
    Get the most recently generated daily content.

    Args:
        content_dir (str): Directory containing JSON files. Defaults to "data/daily_content".

    Returns:
        Dict[str, Any]: Latest content dictionary if any exists, None otherwise.

    Errors:
        json.JSONDecodeError: If JSON file is malformed.
    """
    content_path = Path(content_dir)

    if not content_path.exists():
        return None

    # Find the most recent JSON file
    json_files = sorted(content_path.glob("*.json"), reverse=True)

    if not json_files:
        return None

    try:
        with open(json_files[0]) as f:
            content = json.load(f)
        logger.info(f"Loaded latest content from {json_files[0].name}")
        return content
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON file {json_files[0]}: {str(e)}")
        raise
