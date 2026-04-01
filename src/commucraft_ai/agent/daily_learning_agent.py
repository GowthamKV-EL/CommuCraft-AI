"""Daily learning agent powered by Google Gemini API using LangChain.

This module implements the core AI agent for generating daily learning content.
"""

import json
from datetime import datetime
from typing import Any, Dict

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate

from commucraft_ai.prompts.daily_learning import SYSTEM_PROMPT, get_user_prompt
from commucraft_ai.utils.logger import get_logger
from commucraft_ai.utils.retry_handler import retry_with_backoff

logger = get_logger("daily_learning_agent")


class DailyLearningAgent:
    """AI agent for generating daily professional communication learning content."""

    def __init__(self, google_api_key: str) -> None:
        """
        Initialize the daily learning agent with Google Gemini LLM.

        Args:
            google_api_key (str): Google API key for Gemini access.

        Errors:
            ValueError: If google_api_key is empty or invalid.
        """
        if not google_api_key:
            raise ValueError("google_api_key cannot be empty")

        self.google_api_key = google_api_key

        # Initialize Gemini LLM
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=google_api_key)

        # Create prompt template
        self.prompt_template = ChatPromptTemplate.from_messages(
            [
                ("system", SYSTEM_PROMPT),
                ("human", "{user_prompt}"),
            ]
        )

        logger.info("Daily learning agent initialized successfully")

    @retry_with_backoff(max_retries=3, initial_delay=1.0)
    def generate_daily_content(self, role: str, proficiency_level: str) -> Dict[str, Any]:
        """
        Generate daily learning content using the Gemini LLM.

        Creates a professional paragraph and 10-20 vocabulary words with meanings,
        usage examples, and phonetic pronunciation guides. Uses retry logic with
        exponential backoff for API resilience.

        Args:
            role (str): User's job role (e.g., "sales", "engineering").
            proficiency_level (str): User's language proficiency level (e.g., "intermediate").

        Returns:
            Dict[str, Any]: Dictionary containing date, role, proficiency_level, paragraph, and vocabulary list.

        Errors:
            ValueError: If generated content fails validation.
            Exception: If API call fails after 3 retry attempts.

        Example:
            Input: generate_daily_content("sales", "intermediate")
            Output: {
                "date": "2026-03-24",
                "role": "sales",
                "proficiency_level": "intermediate",
                "paragraph": "...",
                "vocabulary": [...]
            }
        """
        # Get current date
        current_date = datetime.now().strftime("%Y-%m-%d")

        logger.info(f"Generating daily content for {role} at {proficiency_level} level")

        # Get formatted user prompt
        user_prompt = get_user_prompt(role, proficiency_level, current_date)

        # Create and invoke chain
        chain = self.prompt_template | self.llm

        logger.debug("Invoking Gemini LLM for content generation...")
        response = chain.invoke({"user_prompt": user_prompt})

        # Extract content from response
        content_text = response.content

        # Ensure content_text is a string
        if not isinstance(content_text, str):
            content_text = str(content_text)

        logger.debug(f"Received response from LLM: {len(content_text)} characters")

        # Parse JSON from response with robust extraction using brace counting
        try:
            content = self._extract_and_parse_json(content_text)
            logger.info(f"Successfully parsed daily content with {len(content.get('vocabulary', []))} words")
            return content

        except ValueError as e:
            logger.error(f"Failed to parse LLM response: {str(e)}")
            logger.debug(f"Response text: {content_text}")
            raise

    def _extract_and_parse_json(self, text: str) -> Dict[str, Any]:
        """
        Extract and parse JSON from text using brace counting for robustness.

        Finds all balanced JSON objects in the text by counting braces, then attempts
        to parse each one. Returns the first valid JSON that matches the required structure.

        Args:
            text (str): Text potentially containing JSON objects.

        Returns:
            Dict[str, Any]: Parsed JSON object with required keys.

        Errors:
            ValueError: If no valid JSON with required structure is found.
        """
        required_keys = {"date", "role", "proficiency_level", "intro_message", "paragraph", "vocabulary"}

        # Find all potential JSON objects using brace counting
        json_candidates = self._find_json_objects(text)

        if not json_candidates:
            raise ValueError("No JSON objects found in LLM response")

        # Try to parse each candidate
        last_error = None
        for json_str in json_candidates:
            try:
                content = json.loads(json_str)

                # Validate this is the correct structure
                if required_keys.issubset(content.keys()):
                    return content
            except json.JSONDecodeError as e:
                last_error = e
                continue

        # If we get here, no valid JSON was found
        raise ValueError(f"No valid JSON structure found in LLM response. Last error: {str(last_error)}")

    def _find_json_objects(self, text: str) -> list[str]:
        """
        Find all balanced JSON objects in text by counting braces.

        Args:
            text (str): Text potentially containing JSON objects.

        Returns:
            list[str]: List of potential JSON object strings.
        """
        json_objects = []
        in_string = False
        escape_next = False
        brace_count = 0
        start_idx = -1

        for i, char in enumerate(text):
            # Handle escape sequences in strings
            if escape_next:
                escape_next = False
                continue

            if char == "\\" and in_string:
                escape_next = True
                continue

            # Track whether we're inside a string
            if char == '"' and not escape_next:
                in_string = not in_string
                continue

            # Only count braces outside of strings
            if not in_string:
                if char == "{":
                    if brace_count == 0:
                        start_idx = i
                    brace_count += 1
                elif char == "}":
                    brace_count -= 1
                    if brace_count == 0 and start_idx != -1:
                        # Found a complete JSON object
                        json_objects.append(text[start_idx : i + 1])
                        start_idx = -1

        return json_objects
