"""Retry handler with exponential backoff for API calls.

This module provides utilities for retrying failed operations with exponential backoff.
"""

import time
from functools import wraps
from typing import Any, Callable, Optional, TypeVar, cast

from commucraft_ai.utils.logger import get_logger

logger = get_logger("retry_handler")

F = TypeVar("F", bound=Callable[..., Any])


def retry_with_backoff(max_retries: int = 3, initial_delay: float = 1.0) -> Callable[[F], F]:
    """
    Decorator that retries a function with exponential backoff.

    Retries the decorated function up to max_retries times with exponential delays
    between attempts (1s, 2s, 4s, etc.).

    Args:
        max_retries (int): Maximum number of retry attempts. Defaults to 3.
        initial_delay (float): Initial delay in seconds between retries. Defaults to 1.0.

    Returns:
        Callable: Decorated function with retry logic.

    Example:
        Input: @retry_with_backoff(max_retries=3)
               def api_call(): ...
        Output: Function that retries up to 3 times with exponential backoff.
    """

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            delay = initial_delay
            last_exception: Optional[Exception] = None

            for attempt in range(max_retries + 1):
                try:
                    logger.debug(f"Attempt {attempt + 1}/{max_retries + 1} for {func.__name__}")
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries:
                        logger.warning(
                            f"Attempt {attempt + 1} failed for {func.__name__}: {str(e)}. Retrying in {delay}s..."
                        )
                        time.sleep(delay)
                        delay *= 2  # Exponential backoff
                    else:
                        logger.error(f"All {max_retries + 1} attempts failed for {func.__name__}: {str(e)}")

            # Raise the last exception that occurred
            # If we reach here, all retries have been exhausted
            if last_exception is not None:
                raise last_exception
            # This return is unreachable if max_retries >= 0, but satisfies type checker
            return None

        return cast(F, wrapper)

    return decorator
