"""
Unit tests for CommuCraft-AI storage module.

Tests the JSON storage functionality for persisting daily learning content,
user profiles, and communication history.

Args:
    None

Returns:
    None

Errors:
    pytest fixtures provide necessary setup/teardown
"""

import tempfile
from pathlib import Path

import pytest

from src.sc_bot.storage.json_storage import JSONStorage


@pytest.fixture
def temp_storage_dir() -> Path:
    """
    Create temporary directory for test storage.

    Args:
        None

    Returns:
        Path: Temporary directory path

    Errors:
        None
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def storage(temp_storage_dir: Path) -> JSONStorage:
    """
    Create storage instance with temporary directory.

    Args:
        temp_storage_dir (Path): Temporary directory.

    Returns:
        JSONStorage: Storage instance.

    Errors:
        None
    """
    return JSONStorage(temp_storage_dir)


def test_save_and_load_daily_learning(storage: JSONStorage) -> None:
    """
    Test saving and loading daily learning content.

    Args:
        storage (JSONStorage): Storage instance.

    Returns:
        None

    Errors:
        AssertionError: If test fails.
    """
    content = {
        "paragraph": "Test paragraph about professional communication",
        "vocabulary": [{"word": "leverage", "meaning": "to use something to advantage"}],
        "proficiency": "intermediate",
    }

    storage.save_daily_learning(content)
    loaded = storage.load_daily_learning()

    assert loaded is not None
    assert loaded["content"]["paragraph"] == content["paragraph"]
    assert len(loaded["content"]["vocabulary"]) == 1


def test_save_and_load_user_profile(storage: JSONStorage) -> None:
    """
    Test saving and loading user profiles.

    Args:
        storage (JSONStorage): Storage instance.

    Returns:
        None

    Errors:
        AssertionError: If test fails.
    """
    user_id = "test_user_123"
    profile = {"proficiency": "intermediate", "role": "manager", "preferences": {"tone": "professional"}}

    storage.save_user_profile(user_id, profile)
    loaded = storage.load_user_profile(user_id)

    assert loaded is not None
    assert loaded["proficiency"] == "intermediate"
    assert loaded["role"] == "manager"


def test_save_communication_history(storage: JSONStorage) -> None:
    """
    Test saving communication history entries.

    Args:
        storage (JSONStorage): Storage instance.

    Returns:
        None

    Errors:
        AssertionError: If test fails.
    """
    user_id = "test_user_123"
    entry = {"type": "email", "original": "Hi there", "rewritten": "Hello,\n\nI hope this message finds you well"}

    storage.save_communication_history(user_id, entry)
    history = storage.load_communication_history(user_id)

    assert len(history) == 1
    assert history[0]["type"] == "email"


def test_load_communication_history_with_limit(storage: JSONStorage) -> None:
    """
    Test loading communication history with limit.

    Args:
        storage (JSONStorage): Storage instance.

    Returns:
        None

    Errors:
        AssertionError: If test fails.
    """
    user_id = "test_user_123"

    for i in range(5):
        entry = {"type": "email", "original": f"Message {i}", "rewritten": f"Rewritten {i}"}
        storage.save_communication_history(user_id, entry)

    history = storage.load_communication_history(user_id, limit=3)
    assert len(history) == 3


def test_list_files(storage: JSONStorage) -> None:
    """
    Test listing stored files.

    Args:
        storage (JSONStorage): Storage instance.

    Returns:
        None

    Errors:
        AssertionError: If test fails.
    """
    storage.save_daily_learning({"paragraph": "Test", "vocabulary": []})
    storage.save_user_profile("user1", {"proficiency": "intermediate"})

    files = storage.list_files()
    assert len(files) >= 2

    daily_files = storage.list_files("daily_learning_*.json")
    assert len(daily_files) >= 1


def test_save_meeting_prep(storage: JSONStorage) -> None:
    """
    Test saving meeting preparation.

    Args:
        storage (JSONStorage): Storage instance.

    Returns:
        None

    Errors:
        AssertionError: If test fails.
    """
    user_id = "test_user_123"
    prep_data = {
        "meeting_title": "Q1 Review",
        "objective": "Discuss performance",
        "talking_points": ["Achievement 1", "Achievement 2"],
    }

    storage.save_meeting_prep(user_id, prep_data)
    files = storage.list_files("meeting_prep_*.json")

    assert len(files) >= 1


def test_user_profile_not_found(storage: JSONStorage) -> None:
    """
    Test loading non-existent user profile.

    Args:
        storage (JSONStorage): Storage instance.

    Returns:
        None

    Errors:
        AssertionError: If test fails.
    """
    loaded = storage.load_user_profile("nonexistent_user")
    assert loaded is None


def test_daily_learning_not_found(storage: JSONStorage) -> None:
    """
    Test loading non-existent daily learning.

    Args:
        storage (JSONStorage): Storage instance.

    Returns:
        None

    Errors:
        AssertionError: If test fails.
    """
    loaded = storage.load_daily_learning("2000-01-01")
    assert loaded is None
