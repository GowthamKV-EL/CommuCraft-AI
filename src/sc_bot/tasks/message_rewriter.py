"""
Message rewriting task for professional communication improvement.

This module rewrites professional messages (emails, chat, documents) to improve
clarity, tone, and professionalism while preserving original intent.

Args:
    None

Returns:
    None

Errors:
    ValueError: If message validation or rewriting fails.
    Exception: If LLM API calls fail.
"""

import logging
from typing import Any, Optional

from sc_bot.storage.json_storage import JSONStorage

logger = logging.getLogger(__name__)


class MessageRewriterTask:
    """
    Rewrite professional messages for clarity and tone improvement.

    This class handles rewriting various types of business communications
    with support for pseudo-input format.

    Args:
        llm (Any): Language model instance.
        storage (JSONStorage): Storage instance.

    Returns:
        None

    Errors:
        ValueError: If inputs are invalid.
    """

    VALID_COMMUNICATION_TYPES = ["email", "chat", "document", "update", "presentation", "report"]
    VALID_TONES = ["formal", "casual", "professional", "friendly", "assertive"]

    def __init__(self, llm: Any, storage: JSONStorage) -> None:
        """
        Initialize message rewriter task.

        Args:
            llm (Any): Language model instance.
            storage (JSONStorage): Storage instance for saving history.

        Returns:
            None

        Errors:
            ValueError: If parameters are invalid.
        """
        self.llm = llm
        self.storage = storage
        logger.info("MessageRewriterTask initialized")

    def rewrite_message(
        self,
        user_id: str,
        message: str,
        communication_type: str,
        objective: str,
        audience: str,
        key_points: Optional[list[str]] = None,
        desired_tone: str = "professional",
    ) -> dict[str, Any]:
        """
        Rewrite a message with specified parameters.

        Args:
            user_id (str): User identifier.
            message (str): Original message to rewrite.
            communication_type (str): Type of communication (email, chat, etc.).
            objective (str): Goal/objective of the message.
            audience (str): Target audience description.
            key_points (Optional[list[str]]): Important points to emphasize.
            desired_tone (str): Desired tone of the message. Defaults to "professional".

        Returns:
            dict[str, Any]: Rewritten message with analysis and suggestions.

        Errors:
            ValueError: If inputs are invalid.
            Exception: If LLM API call fails.

        Example:
            Input:
                message="we need to discuss the project deadline",
                communication_type="email",
                objective="Request meeting about project timeline",
                audience="Manager",
                desired_tone="professional"
            Output:
                {
                    "original": "...",
                    "rewritten": "I would like to schedule a meeting to discuss the project timeline...",
                    "improvements": ["Added politeness", "Clearer objective", "Professional tone"],
                    "tone_analysis": "professional"
                }
        """
        # Validate inputs
        self._validate_inputs(communication_type, desired_tone, message)

        try:
            # Generate rewritten version
            rewritten = self._generate_rewrite(
                message=message,
                communication_type=communication_type,
                objective=objective,
                audience=audience,
                key_points=key_points,
                desired_tone=desired_tone,
            )

            # Generate improvement analysis
            improvements = self._analyze_improvements(message, rewritten["text"])

            result = {
                "original": message,
                "rewritten": rewritten["text"],
                "communication_type": communication_type,
                "objective": objective,
                "audience": audience,
                "tone": desired_tone,
                "improvements": improvements,
                "alternative_versions": rewritten.get("alternatives", []),
            }

            # Save to history
            self.storage.save_communication_history(user_id, result)
            logger.info(f"Message rewrite saved for user {user_id}")

            return result

        except Exception as e:
            logger.error(f"Failed to rewrite message: {e}")
            raise

    def _validate_inputs(self, communication_type: str, desired_tone: str, message: str) -> None:
        """
        Validate input parameters.

        Args:
            communication_type (str): Type of communication.
            desired_tone (str): Desired tone.
            message (str): Message content.

        Returns:
            None

        Errors:
            ValueError: If validation fails.

        Example:
            Input: communication_type="email", desired_tone="professional", message="Hello"
            Output: None (validation passed)
        """
        if not message or not message.strip():
            raise ValueError("Message cannot be empty")

        if communication_type.lower() not in self.VALID_COMMUNICATION_TYPES:
            raise ValueError(f"Communication type must be one of {self.VALID_COMMUNICATION_TYPES}")

        if desired_tone.lower() not in self.VALID_TONES:
            raise ValueError(f"Tone must be one of {self.VALID_TONES}")

    def _generate_rewrite(
        self,
        message: str,
        communication_type: str,
        objective: str,
        audience: str,
        key_points: Optional[list[str]],
        desired_tone: str,
    ) -> dict[str, Any]:
        """
        Generate rewritten message using LLM.

        Args:
            message (str): Original message.
            communication_type (str): Type of communication.
            objective (str): Message objective.
            audience (str): Target audience.
            key_points (Optional[list[str]]): Key points to include.
            desired_tone (str): Desired tone.

        Returns:
            dict[str, Any]: Rewritten message and alternatives.

        Errors:
            Exception: If LLM call fails.

        Example:
            Input: message="hi, we need to talk about the project"
            Output: {"text": "I would like to discuss the project...", "alternatives": [...]}
        """
        key_points_text = (
            f"Key points to include: {', '.join(key_points)}" if key_points else "No specific points required."
        )

        prompt = f"""You are a professional communication coach. Rewrite the following {communication_type} to:
        - Achieve this objective: {objective}
        - Address this audience: {audience}
        - Use a {desired_tone} tone
        - {key_points_text}
        
        ORIGINAL MESSAGE:
        {message}
        
        Provide:
        1. A professionally rewritten version
        2. 2-3 alternative versions with different approaches
        
        Format your response as JSON with:
        {{
            "rewritten": "main rewritten version",
            "alternatives": ["version 1", "version 2"]
        }}
        
        Return ONLY valid JSON, no other text."""

        try:
            response = self.llm.invoke(prompt)
            import json

            result = json.loads(response)
            return {"text": result.get("rewritten", message), "alternatives": result.get("alternatives", [])}
        except Exception as e:
            logger.error(f"Failed to generate rewrite: {e}")
            raise

    def _analyze_improvements(self, original: str, rewritten: str) -> list[str]:
        """
        Analyze improvements made to the message.

        Args:
            original (str): Original message.
            rewritten (str): Rewritten message.

        Returns:
            list[str]: List of improvements made.

        Errors:
            Exception: If analysis fails.

        Example:
            Input: original="hi, need to talk", rewritten="I would like to schedule a meeting"
            Output: ["Improved politeness", "Clearer structure", "Professional tone"]
        """
        prompt = f"""Analyze the improvements made from the original to rewritten message.
        
        ORIGINAL: {original}
        REWRITTEN: {rewritten}
        
        List 3-5 specific improvements made (clarity, tone, structure, professionalism, etc).
        Return as a JSON array of strings:
        ["improvement 1", "improvement 2", ...]
        
        Return ONLY the JSON array."""

        try:
            response = self.llm.invoke(prompt)
            import json

            return json.loads(response)
        except Exception as e:
            logger.warning(f"Failed to analyze improvements: {e}")
            return ["Message rewritten successfully"]

    def get_communication_history(self, user_id: str, limit: int = 10) -> list[dict[str, Any]]:
        """
        Get communication rewriting history for a user.

        Args:
            user_id (str): User identifier.
            limit (int): Maximum number of entries to retrieve. Defaults to 10.

        Returns:
            list[dict[str, Any]]: List of communication history entries.

        Errors:
            Exception: If storage access fails.

        Example:
            Input: user_id="user123", limit=5
            Output: [{"original": "...", "rewritten": "...", "timestamp": "..."}]
        """
        try:
            return self.storage.load_communication_history(user_id, limit)
        except Exception as e:
            logger.error(f"Failed to load communication history: {e}")
            return []
