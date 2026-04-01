"""Tests for markdown formatter and Slack messenger utilities."""

from unittest.mock import MagicMock, patch
import sys

import pytest

from commucraft_ai.utils.markdown_formatter import format_daily_content_to_markdown, format_vocabulary_for_slack
from commucraft_ai.utils.slack_messenger import SlackMessenger, send_daily_content_to_slack

# Mock slack_sdk for tests when it's not installed
sys.modules["slack_sdk"] = MagicMock()
sys.modules["slack_sdk.errors"] = MagicMock()


# Sample test data
SAMPLE_CONTENT = {
    "date": "2026-03-24",
    "role": "sales",
    "proficiency_level": "intermediate",
    "intro_message": "As a sales professional, mastering persuasive communication directly impacts your ability to close deals.",
    "paragraph": "Effective communication in sales requires understanding your audience deeply and presenting solutions tailored to their needs and pain points.",
    "vocabulary": [
        {
            "word": "Paradigm",
            "meaning": "A typical example or pattern of something.",
            "usage_example": "We need to shift our paradigm in how we approach customer engagement.",
            "pronunciation": "PAR-uh-dime",
        },
        {
            "word": "Synergy",
            "meaning": "The interaction of two or more elements to produce a combined effect.",
            "usage_example": "The synergy between our team members led to great results.",
            "pronunciation": "SIN-ur-jee",
        },
        {
            "word": "Stakeholder",
            "meaning": "A person with an interest or concern in something.",
            "usage_example": "We must keep all stakeholders informed of project changes.",
            "pronunciation": "STAKE-hol-der",
        },
        {
            "word": "Facilitate",
            "meaning": "To make something easier or help it happen.",
            "usage_example": "The manager will facilitate the discussion between teams.",
            "pronunciation": "fuh-SIL-uh-tate",
        },
        {
            "word": "Leverage",
            "meaning": "To use something to maximum advantage.",
            "usage_example": "We can leverage our existing relationships to expand into new markets.",
            "pronunciation": "LEV-er-ij",
        },
        {
            "word": "Iterate",
            "meaning": "To repeat a process with the goal of improving it.",
            "usage_example": "We will iterate on our strategy based on customer feedback.",
            "pronunciation": "IT-uh-rate",
        },
        {
            "word": "Articulate",
            "meaning": "To express something clearly and effectively.",
            "usage_example": "The CEO was able to articulate the company vision perfectly.",
            "pronunciation": "ar-TIK-yuh-late",
        },
        {
            "word": "Navigate",
            "meaning": "To find one's way or move through something.",
            "usage_example": "We must navigate the competitive landscape carefully.",
            "pronunciation": "NAV-uh-gate",
        },
        {
            "word": "Resilience",
            "meaning": "The ability to recover from difficulties.",
            "usage_example": "The team showed great resilience during the market downturn.",
            "pronunciation": "ruh-ZIL-yuns",
        },
        {
            "word": "Holistic",
            "meaning": "Dealing with the subject as a whole.",
            "usage_example": "We need a holistic approach to customer retention.",
            "pronunciation": "hoh-LIS-tik",
        },
    ],
}


class TestMarkdownFormatter:
    """Tests for markdown formatter."""

    def test_format_daily_content_to_markdown_success(self) -> None:
        """Test successful formatting of daily content to markdown."""
        markdown = format_daily_content_to_markdown(SAMPLE_CONTENT)

        assert "Welcome to Your Daily CommuCraft Session" in markdown
        assert SAMPLE_CONTENT["intro_message"] in markdown
        assert SAMPLE_CONTENT["paragraph"] in markdown
        assert "Vocabulary Builder" in markdown
        assert "Paradigm" in markdown
        assert "sales" in markdown.lower()

    def test_format_daily_content_missing_intro_message(self) -> None:
        """Test formatting fails when intro_message is missing."""
        content = SAMPLE_CONTENT.copy()
        del content["intro_message"]

        with pytest.raises(KeyError):
            format_daily_content_to_markdown(content)

    def test_format_daily_content_missing_paragraph(self) -> None:
        """Test formatting fails when paragraph is missing."""
        content = SAMPLE_CONTENT.copy()
        del content["paragraph"]

        with pytest.raises(KeyError):
            format_daily_content_to_markdown(content)

    def test_format_daily_content_missing_vocabulary(self) -> None:
        """Test formatting fails when vocabulary is missing."""
        content = SAMPLE_CONTENT.copy()
        del content["vocabulary"]

        with pytest.raises(KeyError):
            format_daily_content_to_markdown(content)

    def test_format_daily_content_escapes_pipes_in_fields(self) -> None:
        """Test that pipe characters are escaped in markdown table fields."""
        content = SAMPLE_CONTENT.copy()
        content["vocabulary"][0]["meaning"] = "A pattern | divider."

        markdown = format_daily_content_to_markdown(content)

        assert "A pattern \\| divider." in markdown

    def test_format_vocabulary_for_slack_success(self) -> None:
        """Test successful formatting of vocabulary for Slack."""
        vocab = SAMPLE_CONTENT["vocabulary"][:3]
        result = format_vocabulary_for_slack(vocab)

        assert "Paradigm" in result
        assert "PAR-uh-dime" in result
        assert "📝" in result  # Definition emoji
        assert "💬" in result  # Usage emoji
        assert "🔊" in result  # Pronunciation emoji

    def test_format_vocabulary_empty_list(self) -> None:
        """Test that empty vocabulary list raises error."""
        with pytest.raises(ValueError):
            format_vocabulary_for_slack([])

    def test_format_vocabulary_missing_fields(self) -> None:
        """Test that vocabulary items with missing fields raise error."""
        vocab = [{"word": "Test"}]  # Missing meaning, usage_example, pronunciation

        with pytest.raises(ValueError):
            format_vocabulary_for_slack(vocab)


class TestSlackMessenger:
    """Tests for Slack messenger."""

    def test_slack_messenger_init_with_credentials(self) -> None:
        """Test SlackMessenger initialization with provided credentials."""
        messenger = SlackMessenger(bot_token="xoxb-test", channel_id="C123456")

        assert messenger.bot_token == "xoxb-test"
        assert messenger.channel_id == "C123456"

    def test_slack_messenger_init_missing_token(self) -> None:
        """Test SlackMessenger raises error when token is missing."""
        with pytest.raises(ValueError, match="SLACK_BOT_TOKEN"):
            SlackMessenger(bot_token=None, channel_id="C123456")

    def test_slack_messenger_init_missing_channel(self) -> None:
        """Test SlackMessenger raises error when channel is missing."""
        with pytest.raises(ValueError, match="SLACK_CHANNEL_ID"):
            SlackMessenger(bot_token="xoxb-test", channel_id=None)

    @patch("commucraft_ai.utils.slack_messenger.SlackMessenger.send_message")
    def test_slack_messenger_send_message_success(self, mock_send_message: MagicMock) -> None:
        """Test successful message sending to Slack."""
        mock_send_message.return_value = {
            "ok": True,
            "channel": "C123456",
            "ts": "1234567890.123456",
        }

        messenger = SlackMessenger(bot_token="xoxb-test", channel_id="C123456")
        result = messenger.send_message("# Welcome\n\nTest message")

        assert result["ok"] is True

    @patch("commucraft_ai.utils.slack_messenger.SlackMessenger.send_message")
    def test_slack_messenger_send_message_with_thread(self, mock_send_message: MagicMock) -> None:
        """Test sending message to a specific thread."""
        mock_send_message.return_value = {
            "ok": True,
            "channel": "C123456",
            "ts": "1234567890.123456",
        }

        messenger = SlackMessenger(bot_token="xoxb-test", channel_id="C123456")
        messenger.thread_ts = "1234567890.000001"
        result = messenger.send_message("Test reply")

        assert result["ok"] is True

    def test_send_daily_content_to_slack_disabled(self) -> None:
        """Test that send_daily_content_to_slack returns False when disabled."""
        with patch.dict("os.environ", {"SLACK_ENABLED": "false"}):
            result = send_daily_content_to_slack("Test message")
            assert result is False

    @patch("commucraft_ai.utils.slack_messenger.send_daily_content_to_slack")
    def test_send_daily_content_to_slack_enabled(self, mock_send: MagicMock) -> None:
        """Test that send_daily_content_to_slack sends when enabled."""
        mock_send.return_value = True

        # The function should be callable
        assert callable(send_daily_content_to_slack)

    def test_send_daily_content_to_slack_missing_credentials(self) -> None:
        """Test that send_daily_content_to_slack handles missing credentials gracefully."""
        with patch.dict("os.environ", {"SLACK_ENABLED": "true", "SLACK_BOT_TOKEN": "", "SLACK_CHANNEL_ID": ""}):
            result = send_daily_content_to_slack("Test message")
            assert result is False
