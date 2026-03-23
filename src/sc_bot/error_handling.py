"""
Error handling and validation utilities for CommuCraft-AI.

This module provides custom exceptions, error handlers, and validation utilities
with escalation logic for unclear user intents.

Args:
    None

Returns:
    None

Errors:
    Various custom exceptions for domain-specific errors.
"""

import logging
from enum import Enum
from typing import Any, Callable, Optional, TypeVar

logger = logging.getLogger(__name__)


# Custom Exceptions
class CommuCraftException(Exception):
    """Base exception for CommuCraft-AI."""

    pass


class ValidationError(CommuCraftException):
    """Raised when input validation fails."""

    pass


class ConfigurationError(CommuCraftException):
    """Raised when configuration is invalid."""

    pass


class StorageError(CommuCraftException):
    """Raised when storage operations fail."""

    pass


class LLMError(CommuCraftException):
    """Raised when LLM API calls fail."""

    pass


class EscalationRequiredError(CommuCraftException):
    """Raised when user intent is unclear and needs clarification."""

    pass


class EscalationLevel(str, Enum):
    """Escalation levels for unclear requests."""

    CLARIFICATION_NEEDED = "clarification_needed"
    INTENT_AMBIGUOUS = "intent_ambiguous"
    INSUFFICIENT_CONTEXT = "insufficient_context"
    INVALID_REQUEST = "invalid_request"


class EscalationHandler:
    """
    Handle escalation of unclear or invalid requests.

    This class manages the escalation process when the system cannot
    confidently determine user intent or has insufficient context.

    Args:
        None

    Returns:
        None

    Errors:
        None
    """

    def __init__(self) -> None:
        """
        Initialize escalation handler.

        Args:
            None

        Returns:
            None

        Errors:
            None
        """
        self.escalations = []

    def escalate(self, level: EscalationLevel, message: str, context: Optional[dict[str, Any]] = None) -> None:
        """
        Log an escalation with details.

        Args:
            level (EscalationLevel): Escalation level.
            message (str): Description of the issue.
            context (Optional[dict[str, Any]]): Additional context information.

        Returns:
            None

        Errors:
            None

        Example:
            Input: level=EscalationLevel.CLARIFICATION_NEEDED, message="Email objective unclear"
            Output: Escalation logged
        """
        escalation = {
            "level": level.value,
            "message": message,
            "context": context or {},
            "timestamp": __import__("datetime").datetime.now().isoformat(),
        }

        self.escalations.append(escalation)
        logger.warning(f"Escalation [{level.value}]: {message}")

    def get_clarification_prompt(self, level: EscalationLevel) -> str:
        """
        Get user-friendly clarification prompt.

        Args:
            level (EscalationLevel): Escalation level.

        Returns:
            str: Clarification prompt for user.

        Errors:
            None

        Example:
            Input: EscalationLevel.CLARIFICATION_NEEDED
            Output: "I need some clarification to help you better..."
        """
        prompts = {
            EscalationLevel.CLARIFICATION_NEEDED: """I need some clarification to help you better:

Could you provide more details about:
- Your specific goal or objective
- Who the intended audience is
- Any key points or information that must be included
- The desired tone or style

This will help me provide better assistance.""",
            EscalationLevel.INTENT_AMBIGUOUS: """Your request could be interpreted in multiple ways. Could you clarify:

- What specifically are you trying to achieve?
- Is this for an email, chat message, document, or something else?
- Who will be reading/listening to this?

Please provide more context so I can assist you more effectively.""",
            EscalationLevel.INSUFFICIENT_CONTEXT: """I need more context to help you properly:

- What is the background or situation?
- Are there any previous interactions or decisions that matter?
- What are the potential concerns or sensitivities?

Please share relevant background information.""",
            EscalationLevel.INVALID_REQUEST: """I'm unable to process this request. Please ensure:

- Your input is clear and complete
- You're asking for help with a communication task
- The information provided is valid and relevant

What would you like help with? (Daily learning, message rewriting, or meeting prep?)""",
        }

        return prompts.get(level, "Could you please provide more details about your request?")

    def get_recent_escalations(self, limit: int = 10) -> list[dict[str, Any]]:
        """
        Get recent escalations.

        Args:
            limit (int): Maximum number of escalations to return. Defaults to 10.

        Returns:
            list[dict[str, Any]]: List of recent escalations.

        Errors:
            None

        Example:
            Input: limit=5
            Output: [{"level": "clarification_needed", "message": "...", "timestamp": "..."}]
        """
        return self.escalations[-limit:]


class InputValidator:
    """
    Validate user inputs with detailed error messages.

    This class provides validation methods for different types of inputs
    with clear error messages for user feedback.

    Args:
        None

    Returns:
        None

    Errors:
        ValidationError: If validation fails.
    """

    @staticmethod
    def validate_email_content(message: str, min_length: int = 5, max_length: int = 5000) -> None:
        """
        Validate email message content.

        Args:
            message (str): Message content to validate.
            min_length (int): Minimum message length. Defaults to 5.
            max_length (int): Maximum message length. Defaults to 5000.

        Returns:
            None

        Errors:
            ValidationError: If validation fails.

        Example:
            Input: message="Hello world"
            Output: None (validation passed)
        """
        if not message or not message.strip():
            raise ValidationError("Message cannot be empty")

        if len(message) < min_length:
            raise ValidationError(f"Message too short. Minimum {min_length} characters required")

        if len(message) > max_length:
            raise ValidationError(f"Message too long. Maximum {max_length} characters allowed")

    @staticmethod
    def validate_meeting_details(title: str, objective: str, audience: str, discussion_points: list[str]) -> None:
        """
        Validate meeting preparation inputs.

        Args:
            title (str): Meeting title.
            objective (str): Meeting objective.
            audience (str): Audience description.
            discussion_points (list[str]): Discussion points.

        Returns:
            None

        Errors:
            ValidationError: If validation fails.

        Example:
            Input: title="Review", objective="Performance discussion"
            Output: None (validation passed)
        """
        if not title or not title.strip():
            raise ValidationError("Meeting title is required")

        if not objective or not objective.strip():
            raise ValidationError("Meeting objective is required")

        if not audience or not audience.strip():
            raise ValidationError("Audience description is required")

        if not discussion_points or len(discussion_points) == 0:
            raise ValidationError("At least one discussion point is required")

        if len(discussion_points) > 20:
            raise ValidationError("Too many discussion points. Maximum 20 allowed")

    @staticmethod
    def validate_proficiency_level(level: str) -> None:
        """
        Validate proficiency level.

        Args:
            level (str): Proficiency level to validate.

        Returns:
            None

        Errors:
            ValidationError: If validation fails.

        Example:
            Input: "intermediate"
            Output: None (validation passed)
        """
        valid_levels = ["beginner", "intermediate", "advanced"]
        if level.lower() not in valid_levels:
            raise ValidationError(f"Proficiency level must be one of {valid_levels}, got {level}")

    @staticmethod
    def validate_communication_type(comm_type: str) -> None:
        """
        Validate communication type.

        Args:
            comm_type (str): Communication type to validate.

        Returns:
            None

        Errors:
            ValidationError: If validation fails.

        Example:
            Input: "email"
            Output: None (validation passed)
        """
        valid_types = ["email", "chat", "document", "update", "presentation", "report"]
        if comm_type.lower() not in valid_types:
            raise ValidationError(f"Communication type must be one of {valid_types}, got {comm_type}")

    @staticmethod
    def validate_tone(tone: str) -> None:
        """
        Validate communication tone.

        Args:
            tone (str): Tone to validate.

        Returns:
            None

        Errors:
            ValidationError: If validation fails.

        Example:
            Input: "professional"
            Output: None (validation passed)
        """
        valid_tones = ["formal", "casual", "professional", "friendly", "assertive"]
        if tone.lower() not in valid_tones:
            raise ValidationError(f"Tone must be one of {valid_tones}, got {tone}")


def handle_errors(func: Callable) -> Callable:
    """
    Decorator for consistent error handling.

    Args:
        func (Callable): Function to decorate.

    Returns:
        Callable: Decorated function with error handling.

    Errors:
        None

    Example:
        Input: @handle_errors decorator
        Output: Function with try-except wrapping
    """

    def wrapper(*args: Any, **kwargs: Any) -> Any:
        """
        Wrapper function for error handling.

        Args:
            *args: Positional arguments.
            **kwargs: Keyword arguments.

        Returns:
            Any: Function result or error response.

        Errors:
            None
        """
        try:
            return func(*args, **kwargs)
        except ValidationError as e:
            logger.error(f"Validation error in {func.__name__}: {e}")
            raise
        except LLMError as e:
            logger.error(f"LLM error in {func.__name__}: {e}")
            raise
        except StorageError as e:
            logger.error(f"Storage error in {func.__name__}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {e}", exc_info=True)
            raise CommuCraftException(f"Error in {func.__name__}: {e}") from e

    return wrapper


T = TypeVar("T")


def safe_execute(func: Callable[..., T], *args: Any, fallback: Optional[T] = None, **kwargs: Any) -> T:
    """
    Safely execute a function with fallback value.

    Args:
        func (Callable): Function to execute.
        *args: Positional arguments.
        fallback (Optional[T]): Fallback value if execution fails. Defaults to None.
        **kwargs: Keyword arguments.

    Returns:
        T: Function result or fallback value.

    Errors:
        None

    Example:
        Input: func=get_data, fallback={}
        Output: Function result or empty dict if error occurs
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        logger.warning(f"Safe execution failed for {func.__name__}: {e}. Using fallback.")
        return fallback
