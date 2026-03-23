"""
Pytest configuration and shared fixtures for CommuCraft-AI tests.

Args:
    None

Returns:
    None

Errors:
    None
"""

import tempfile
from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def temp_dir() -> Path:
    """
    Create a temporary directory for test data.

    Args:
        None

    Returns:
        Path: Temporary directory path.

    Errors:
        None
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture(autouse=True)
def reset_test_environment() -> None:
    """
    Reset test environment between tests.

    Args:
        None

    Returns:
        None

    Errors:
        None
    """
    yield
    # Cleanup happens automatically
