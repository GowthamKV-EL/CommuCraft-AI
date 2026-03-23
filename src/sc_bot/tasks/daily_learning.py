"""
Daily learning task for vocabulary and professional communication improvement.

This module generates daily learning content including a professional paragraph
and 10-20 vocabulary words with meanings and audio pronunciation support.

Args:
    None

Returns:
    None

Errors:
    ValueError: If proficiency level or input validation fails.
    Exception: If LLM API calls fail.
"""

import json
import logging
from datetime import datetime
from typing import Any, Optional

from sc_bot.config import settings
from sc_bot.utils.google_tts import GoogleTextToSpeech

logger = logging.getLogger(__name__)


class DailyLearningTask:
    """
    Generate and manage daily learning content for professional communication.

    This class creates daily learning paragraphs and vocabulary lists based on
    user proficiency level and optional role focus.

    Args:
        llm: Language model instance for generating content.
        storage: Storage instance for persisting content.
        tts (Optional[GoogleTextToSpeech]): Text-to-speech service for audio.

    Returns:
        None

    Errors:
        ValueError: If input validation fails.
    """

    def __init__(self, llm: Any, storage: Any, tts: Optional[GoogleTextToSpeech] = None) -> None:
        """
        Initialize daily learning task.

        Args:
            llm (Any): Language model instance.
            storage (Any): Storage instance.
            tts (Optional[GoogleTextToSpeech]): Text-to-speech service. Defaults to None.

        Returns:
            None

        Errors:
            ValueError: If parameters are invalid.
        """
        self.llm = llm
        self.storage = storage
        self.tts = tts
        self.proficiency_level = settings.user_proficiency_level
        self.role_focus = settings.user_role_focus
        logger.info(f"DailyLearningTask initialized for {self.proficiency_level} level")

    def generate_daily_content(self) -> dict[str, Any]:
        """
        Generate daily learning content with paragraph and vocabulary.

        Args:
            None

        Returns:
            dict[str, Any]: Daily learning content with paragraph, vocabulary, and audio URLs.

        Errors:
            ValueError: If content generation fails.
            Exception: If LLM API call fails.

        Example:
            Input: None
            Output: {
                "paragraph": "...",
                "vocabulary": [
                    {"word": "leverage", "meaning": "...", "audio_url": "..."}
                ],
                "proficiency": "intermediate",
                "generated_at": "2024-03-23T09:00:00"
            }
        """
        try:
            # Generate paragraph
            paragraph = self._generate_paragraph()
            logger.info("Daily paragraph generated")

            # Extract and generate vocabulary
            vocabulary_list = self._generate_vocabulary(paragraph)
            logger.info(f"Generated {len(vocabulary_list)} vocabulary items")

            # Generate audio for each word
            if self.tts:
                for word_item in vocabulary_list:
                    audio_url = self.tts.synthesize_speech(word_item["word"])
                    word_item["audio_url"] = audio_url

            content = {
                "paragraph": paragraph,
                "vocabulary": vocabulary_list,
                "proficiency": self.proficiency_level,
                "role_focus": self.role_focus,
                "generated_at": datetime.now().isoformat(),
            }

            # Save content
            self.storage.save_daily_learning(content)
            return content

        except Exception as e:
            logger.error(f"Failed to generate daily content: {e}")
            raise

    def _generate_paragraph(self) -> str:
        """
        Generate a professional paragraph using LLM.

        Args:
            None

        Returns:
            str: A professional paragraph appropriate for the proficiency level.

        Errors:
            Exception: If LLM call fails.

        Example:
            Input: None
            Output: "Effective communication requires clarity, conciseness, and consideration..."
        """
        prompt = f"""Generate a professional, single paragraph (150-200 words) focused on business communication 
        for someone with {self.proficiency_level} English proficiency{f" working in {self.role_focus}" if self.role_focus != "general" else ""}.
        The paragraph should teach practical communication concepts while being engaging and relatable.
        Write only the paragraph, no additional text."""

        try:
            response = self.llm.invoke(prompt)
            return response
        except Exception as e:
            logger.error(f"Failed to generate paragraph: {e}")
            raise

    def _generate_vocabulary(self, paragraph: str) -> list[dict[str, str]]:
        """
        Extract and generate vocabulary from the paragraph.

        Args:
            paragraph (str): The paragraph to extract vocabulary from.

        Returns:
            list[dict[str, str]]: List of vocabulary items with word and meaning.

        Errors:
            Exception: If vocabulary generation fails.

        Example:
            Input: "Effective communication requires clarity..."
            Output: [
                {"word": "leverage", "meaning": "to use something to maximum advantage", "part_of_speech": "verb"},
                {"word": "synergy", "meaning": "the interaction of two or more elements...", "part_of_speech": "noun"}
            ]
        """
        prompt = f"""From this paragraph, extract 10-20 professional business vocabulary words suitable for 
        {self.proficiency_level} English learners. For each word, provide:
        1. The word
        2. Part of speech
        3. Clear, concise meaning (one sentence max)
        4. A usage example in professional context
        
        Paragraph: {paragraph}
        
        Return as JSON array with this structure:
        [{{"word": "...", "part_of_speech": "...", "meaning": "...", "example": "..."}}]
        
        Return ONLY the JSON array, no other text."""

        try:
            response = self.llm.invoke(prompt)
            # Parse JSON response
            vocabulary_list = json.loads(response)
            logger.info(f"Generated {len(vocabulary_list)} vocabulary items")
            return vocabulary_list
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse vocabulary JSON: {e}")
            raise ValueError(f"Invalid vocabulary format: {e}")
        except Exception as e:
            logger.error(f"Failed to generate vocabulary: {e}")
            raise

    def get_today_learning(self) -> Optional[dict[str, Any]]:
        """
        Get today's learning content from storage.

        Args:
            None

        Returns:
            dict[str, Any] | None: Today's learning content or None if not generated.

        Errors:
            Exception: If storage access fails.

        Example:
            Input: None
            Output: {"paragraph": "...", "vocabulary": [...], "generated_at": "..."}
        """
        try:
            content = self.storage.load_daily_learning()
            return content.get("content") if content else None
        except Exception as e:
            logger.error(f"Failed to load today's learning: {e}")
            return None
