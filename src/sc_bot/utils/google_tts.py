"""
Google Text-to-Speech integration for audio pronunciation support.

This module provides audio synthesis for vocabulary words using Google's
Text-to-Speech API.

Args:
    None

Returns:
    None

Errors:
    Exception: If Google API calls fail.
"""

import logging
from pathlib import Path
from typing import Optional

from google.cloud import texttospeech

from sc_bot.config import settings

logger = logging.getLogger(__name__)


class GoogleTextToSpeech:
    """
    Generate audio pronunciation for vocabulary using Google TTS.

    This class wraps Google Cloud Text-to-Speech API to create audio files
    for word pronunciation support in daily learning.

    Args:
        output_dir (Optional[Path]): Directory to save audio files. Uses data_dir if None.

    Returns:
        None

    Errors:
        Exception: If API initialization fails.
    """

    def __init__(self, output_dir: Optional[Path] = None) -> None:
        """
        Initialize Google Text-to-Speech client.

        Args:
            output_dir (Optional[Path]): Directory for audio files. Defaults to None.

        Returns:
            None

        Errors:
            Exception: If client initialization fails.
        """
        try:
            self.client = texttospeech.TextToSpeechClient()
            self.output_dir = output_dir or settings.get_data_dir() / "audio"
            self.output_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"GoogleTextToSpeech initialized with output dir: {self.output_dir}")
        except Exception as e:
            logger.error(f"Failed to initialize Google TTS client: {e}")
            raise

    def synthesize_speech(
        self, text: str, language_code: Optional[str] = None, voice_name: Optional[str] = None
    ) -> str:
        """
        Synthesize speech for given text and save audio file.

        Args:
            text (str): Text to synthesize.
            language_code (Optional[str]): Language code (e.g., 'en-US'). Defaults to settings value.
            voice_name (Optional[str]): Voice name. Defaults to settings value.

        Returns:
            str: Path to the generated audio file.

        Errors:
            Exception: If API call fails or file write fails.

        Example:
            Input: text="leverage", language_code="en-US"
            Output: "/data/audio/leverage_en-US.mp3"
        """
        language_code = language_code or settings.tts_language_code
        voice_name = voice_name or settings.tts_voice_name

        try:
            # Create synthesis input
            synthesis_input = texttospeech.SynthesisInput(text=text)

            # Build voice
            voice = texttospeech.VoiceSelectionParams(
                language_code=language_code,
                name=voice_name,
            )

            # Configure audio encoding
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                speaking_rate=0.9,  # Slightly slower for clarity
            )

            # Call API
            response = self.client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config,
            )

            # Save audio file
            safe_filename = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in text).lower()
            output_path = self.output_dir / f"{safe_filename}_{language_code}.mp3"

            with open(output_path, "wb") as out:
                out.write(response.audio_content)

            logger.info(f"Audio synthesized for '{text}' at {output_path}")
            return str(output_path)

        except Exception as e:
            logger.error(f"Failed to synthesize speech for '{text}': {e}")
            raise

    def synthesize_batch(
        self, words: list[str], language_code: Optional[str] = None, voice_name: Optional[str] = None
    ) -> dict[str, str]:
        """
        Synthesize speech for multiple words.

        Args:
            words (list[str]): List of words to synthesize.
            language_code (Optional[str]): Language code. Defaults to settings value.
            voice_name (Optional[str]): Voice name. Defaults to settings value.

        Returns:
            dict[str, str]: Mapping of word to audio file path.

        Errors:
            Exception: If any API call fails.

        Example:
            Input: words=["leverage", "synergy", "optimize"]
            Output: {"leverage": "/data/audio/leverage.mp3", "synergy": "/data/audio/synergy.mp3", ...}
        """
        results = {}

        for word in words:
            try:
                audio_path = self.synthesize_speech(word, language_code, voice_name)
                results[word] = audio_path
            except Exception as e:
                logger.warning(f"Failed to synthesize '{word}': {e}")
                results[word] = None

        logger.info(f"Batch synthesis completed: {len([p for p in results.values() if p])} of {len(words)} successful")
        return results

    def get_audio_path(self, text: str, language_code: Optional[str] = None) -> Path:
        """
        Get the expected audio file path for a text without synthesizing.

        Args:
            text (str): Text to get path for.
            language_code (Optional[str]): Language code. Defaults to settings value.

        Returns:
            Path: Expected audio file path.

        Errors:
            None

        Example:
            Input: text="leverage"
            Output: Path("/data/audio/leverage_en-US.mp3")
        """
        language_code = language_code or settings.tts_language_code
        safe_filename = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in text).lower()
        return self.output_dir / f"{safe_filename}_{language_code}.mp3"

    def audio_exists(self, text: str, language_code: Optional[str] = None) -> bool:
        """
        Check if audio file already exists for given text.

        Args:
            text (str): Text to check.
            language_code (Optional[str]): Language code. Defaults to settings value.

        Returns:
            bool: True if audio file exists.

        Errors:
            None

        Example:
            Input: text="leverage"
            Output: True or False
        """
        audio_path = self.get_audio_path(text, language_code)
        return audio_path.exists()
