"""
Unit tests for CommuCraft-AI error handling and validation.

Tests the error handling, validation, and escalation mechanisms.

Args:
    None

Returns:
    None

Errors:
    pytest fixtures and assertions
"""

import pytest

from src.sc_bot.error_handling import (
    EscalationHandler,
    EscalationLevel,
    InputValidator,
    ValidationError,
    safe_execute,
)


def test_input_validator_email_content_valid() -> None:
    """
    Test valid email content validation.

    Args:
        None

    Returns:
        None

    Errors:
        AssertionError: If test fails.
    """
    valid_message = "This is a valid email message with sufficient content"
    InputValidator.validate_email_content(valid_message)  # Should not raise


def test_input_validator_email_content_empty() -> None:
    """
    Test empty email content validation.

    Args:
        None

    Returns:
        None

    Errors:
        AssertionError: If test fails.
    """
    with pytest.raises(ValidationError):
        InputValidator.validate_email_content("")


def test_input_validator_email_content_too_short() -> None:
    """
    Test too-short email content validation.

    Args:
        None

    Returns:
        None

    Errors:
        AssertionError: If test fails.
    """
    with pytest.raises(ValidationError):
        InputValidator.validate_email_content("Hi")


def test_input_validator_communication_type_valid() -> None:
    """
    Test valid communication type validation.

    Args:
        None

    Returns:
        None

    Errors:
        AssertionError: If test fails.
    """
    InputValidator.validate_communication_type("email")  # Should not raise
    InputValidator.validate_communication_type("chat")  # Should not raise


def test_input_validator_communication_type_invalid() -> None:
    """
    Test invalid communication type validation.

    Args:
        None

    Returns:
        None

    Errors:
        AssertionError: If test fails.
    """
    with pytest.raises(ValidationError):
        InputValidator.validate_communication_type("invalid_type")


def test_input_validator_tone_valid() -> None:
    """
    Test valid tone validation.

    Args:
        None

    Returns:
        None

    Errors:
        AssertionError: If test fails.
    """
    InputValidator.validate_tone("professional")  # Should not raise
    InputValidator.validate_tone("friendly")  # Should not raise


def test_input_validator_tone_invalid() -> None:
    """
    Test invalid tone validation.

    Args:
        None

    Returns:
        None

    Errors:
        AssertionError: If test fails.
    """
    with pytest.raises(ValidationError):
        InputValidator.validate_tone("weird_tone")


def test_input_validator_meeting_details_valid() -> None:
    """
    Test valid meeting details validation.

    Args:
        None

    Returns:
        None

    Errors:
        AssertionError: If test fails.
    """
    InputValidator.validate_meeting_details(
        title="Quarterly Review",
        objective="Discuss Q1 performance",
        audience="Manager",
        discussion_points=["Achievements", "Growth areas"],
    )  # Should not raise


def test_input_validator_meeting_details_missing_title() -> None:
    """
    Test meeting details validation with missing title.

    Args:
        None

    Returns:
        None

    Errors:
        AssertionError: If test fails.
    """
    with pytest.raises(ValidationError):
        InputValidator.validate_meeting_details(
            title="",
            objective="Discuss performance",
            audience="Manager",
            discussion_points=["Point 1"],
        )


def test_input_validator_meeting_details_no_points() -> None:
    """
    Test meeting details validation with no discussion points.

    Args:
        None

    Returns:
        None

    Errors:
        AssertionError: If test fails.
    """
    with pytest.raises(ValidationError):
        InputValidator.validate_meeting_details(
            title="Meeting",
            objective="Discuss something",
            audience="Team",
            discussion_points=[],
        )


def test_escalation_handler_escalate() -> None:
    """
    Test escalation handler logging.

    Args:
        None

    Returns:
        None

    Errors:
        AssertionError: If test fails.
    """
    handler = EscalationHandler()
    handler.escalate(EscalationLevel.CLARIFICATION_NEEDED, "Email objective unclear")

    escalations = handler.get_recent_escalations()
    assert len(escalations) == 1
    assert escalations[0]["message"] == "Email objective unclear"


def test_escalation_handler_clarification_prompt() -> None:
    """
    Test escalation handler clarification prompt.

    Args:
        None

    Returns:
        None

    Errors:
        AssertionError: If test fails.
    """
    handler = EscalationHandler()
    prompt = handler.get_clarification_prompt(EscalationLevel.CLARIFICATION_NEEDED)

    assert "clarification" in prompt.lower()
    assert len(prompt) > 0


def test_escalation_handler_ambiguous_prompt() -> None:
    """
    Test escalation handler ambiguous intent prompt.

    Args:
        None

    Returns:
        None

    Errors:
        AssertionError: If test fails.
    """
    handler = EscalationHandler()
    prompt = handler.get_clarification_prompt(EscalationLevel.INTENT_AMBIGUOUS)

    assert "interpreted" in prompt.lower() or "ambiguous" in prompt.lower()


def test_safe_execute_success() -> None:
    """
    Test safe execution with successful function.

    Args:
        None

    Returns:
        None

    Errors:
        AssertionError: If test fails.
    """

    def successful_func() -> str:
        return "Success"

    result = safe_execute(successful_func)
    assert result == "Success"


def test_safe_execute_with_fallback() -> None:
    """
    Test safe execution with fallback on error.

    Args:
        None

    Returns:
        None

    Errors:
        AssertionError: If test fails.
    """

    def failing_func() -> str:
        raise ValueError("Test error")

    result = safe_execute(failing_func, fallback="Fallback value")
    assert result == "Fallback value"


def test_safe_execute_with_args() -> None:
    """
    Test safe execution with arguments.

    Args:
        None

    Returns:
        None

    Errors:
        AssertionError: If test fails.
    """

    def add_numbers(a: int, b: int) -> int:
        return a + b

    result = safe_execute(add_numbers, 5, 3)
    assert result == 8


def test_proficiency_level_validation_valid() -> None:
    """
    Test valid proficiency level validation.

    Args:
        None

    Returns:
        None

    Errors:
        AssertionError: If test fails.
    """
    InputValidator.validate_proficiency_level("beginner")  # Should not raise
    InputValidator.validate_proficiency_level("intermediate")  # Should not raise
    InputValidator.validate_proficiency_level("advanced")  # Should not raise


def test_proficiency_level_validation_invalid() -> None:
    """
    Test invalid proficiency level validation.

    Args:
        None

    Returns:
        None

    Errors:
        AssertionError: If test fails.
    """
    with pytest.raises(ValidationError):
        InputValidator.validate_proficiency_level("expert")
