"""Tests for the daily storage module."""

import json
import pytest
import tempfile
from pathlib import Path
from typing import Dict, Any

from commucraft_ai.storage.daily_storage import (
    DailyContentValidator,
    save_daily_content,
    load_daily_content,
    get_latest_content,
)


@pytest.fixture
def valid_content() -> Dict[str, Any]:
    """Provide a valid daily content structure for testing."""
    return {
        "date": "2026-03-24",
        "role": "sales",
        "proficiency_level": "intermediate",
        "intro_message": "As a sales professional, mastering communication is essential.",
        "paragraph": "This is a test paragraph about professional communication. " * 3,
        "vocabulary": [
            {
                "word": f"word{i}",
                "meaning": f"Meaning of word {i}",
                "usage_example": f"Example sentence with word{i}.",
                "pronunciation": f"WORD-{i}",
            }
            for i in range(1, 16)
        ],
    }


@pytest.fixture
def temp_content_dir() -> str:
    """Provide a temporary directory for storing test content."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


def test_validator_valid_content(valid_content: Dict[str, Any]) -> None:
    """Test that validator accepts valid content."""
    assert DailyContentValidator.validate(valid_content) is True


def test_validator_missing_required_field(valid_content: Dict[str, Any]) -> None:
    """Test that validator rejects content missing required fields."""
    del valid_content["paragraph"]
    with pytest.raises(ValueError, match="Missing required field"):
        DailyContentValidator.validate(valid_content)


def test_validator_empty_paragraph(valid_content: Dict[str, Any]) -> None:
    """Test that validator rejects empty paragraph."""
    valid_content["paragraph"] = ""
    with pytest.raises(ValueError, match="Paragraph must be a non-empty string"):
        DailyContentValidator.validate(valid_content)


def test_validator_vocabulary_too_short(valid_content: Dict[str, Any]) -> None:
    """Test that validator rejects vocabulary with less than 10 words."""
    valid_content["vocabulary"] = valid_content["vocabulary"][:5]
    with pytest.raises(ValueError, match="10-20 words"):
        DailyContentValidator.validate(valid_content)


def test_validator_vocabulary_too_long(valid_content: Dict[str, Any]) -> None:
    """Test that validator rejects vocabulary with more than 20 words."""
    valid_content["vocabulary"] = [
        {
            "word": f"word{i}",
            "meaning": f"Meaning {i}",
            "usage_example": f"Example {i}",
            "pronunciation": f"WORD-{i}",
        }
        for i in range(1, 25)
    ]
    with pytest.raises(ValueError, match="10-20 words"):
        DailyContentValidator.validate(valid_content)


def test_validator_missing_word_field(valid_content: Dict[str, Any]) -> None:
    """Test that validator rejects word missing required field."""
    del valid_content["vocabulary"][0]["meaning"]
    with pytest.raises(ValueError, match="missing required field"):
        DailyContentValidator.validate(valid_content)


def test_validator_empty_word_field(valid_content: Dict[str, Any]) -> None:
    """Test that validator rejects word with empty field."""
    valid_content["vocabulary"][0]["word"] = ""
    with pytest.raises(ValueError, match="must be non-empty string"):
        DailyContentValidator.validate(valid_content)


def test_save_daily_content_success(valid_content: Dict[str, Any], temp_content_dir: str) -> None:
    """Test successful saving of daily content."""
    file_path = save_daily_content(valid_content, output_dir=temp_content_dir)

    assert file_path.exists()
    assert file_path.name == "2026-03-24.json"

    # Verify saved content
    with open(file_path) as f:
        saved_content = json.load(f)

    assert saved_content == valid_content


def test_save_daily_content_creates_directory(valid_content: Dict[str, Any]) -> None:
    """Test that save creates output directory if it doesn't exist."""
    with tempfile.TemporaryDirectory() as tmpdir:
        new_dir = Path(tmpdir) / "nested" / "content" / "dir"
        file_path = save_daily_content(valid_content, output_dir=str(new_dir))

        assert new_dir.exists()
        assert file_path.exists()


def test_save_daily_content_regenerate(valid_content: Dict[str, Any], temp_content_dir: str) -> None:
    """Test that saving overwrites existing content for same date (regenerate)."""
    # Save initial content
    save_daily_content(valid_content, output_dir=temp_content_dir)

    # Modify and save again
    valid_content["paragraph"] = "Modified paragraph for testing regeneration."
    file_path = save_daily_content(valid_content, output_dir=temp_content_dir)

    # Verify overwritten content
    with open(file_path) as f:
        saved_content = json.load(f)

    assert saved_content["paragraph"] == "Modified paragraph for testing regeneration."


def test_save_daily_content_validation_failure(valid_content: Dict[str, Any], temp_content_dir: str) -> None:
    """Test that save fails if content is invalid."""
    del valid_content["vocabulary"]
    with pytest.raises(ValueError):
        save_daily_content(valid_content, output_dir=temp_content_dir)


def test_load_daily_content_success(valid_content: Dict[str, Any], temp_content_dir: str) -> None:
    """Test successful loading of daily content."""
    save_daily_content(valid_content, output_dir=temp_content_dir)

    loaded_content = load_daily_content("2026-03-24", content_dir=temp_content_dir)

    assert loaded_content is not None
    assert loaded_content == valid_content


def test_load_daily_content_not_found(temp_content_dir: str) -> None:
    """Test that loading non-existent content returns None."""
    loaded_content = load_daily_content("2999-12-31", content_dir=temp_content_dir)
    assert loaded_content is None


def test_load_daily_content_malformed_json(temp_content_dir: str) -> None:
    """Test that loading malformed JSON raises error."""
    content_path = Path(temp_content_dir)
    content_path.mkdir(exist_ok=True)

    # Write malformed JSON
    with open(content_path / "2026-03-24.json", "w") as f:
        f.write("{invalid json")

    with pytest.raises(json.JSONDecodeError):
        load_daily_content("2026-03-24", content_dir=temp_content_dir)


def test_get_latest_content_success(valid_content: Dict[str, Any], temp_content_dir: str) -> None:
    """Test retrieving the most recent content."""
    # Save multiple contents
    valid_content["date"] = "2026-03-22"
    save_daily_content(valid_content, output_dir=temp_content_dir)

    valid_content["date"] = "2026-03-24"
    save_daily_content(valid_content, output_dir=temp_content_dir)

    latest_content = get_latest_content(content_dir=temp_content_dir)

    assert latest_content is not None
    assert latest_content["date"] == "2026-03-24"


def test_get_latest_content_empty_directory(temp_content_dir: str) -> None:
    """Test that getting latest content from empty directory returns None."""
    latest_content = get_latest_content(content_dir=temp_content_dir)
    assert latest_content is None


def test_get_latest_content_directory_not_exists() -> None:
    """Test that getting latest content from non-existent directory returns None."""
    latest_content = get_latest_content(content_dir="/non/existent/path")
    assert latest_content is None
