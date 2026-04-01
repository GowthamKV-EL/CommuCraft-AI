"""Tests for the daily learning agent module."""

import pytest
from unittest.mock import patch, MagicMock

from commucraft_ai.agent.daily_learning_agent import DailyLearningAgent


@pytest.fixture
def mock_google_api_key() -> str:
    """Provide a mock Google API key for testing."""
    return "test_key_12345"


@pytest.fixture
def sample_llm_response() -> str:
    """Provide a sample LLM response for testing."""
    return """{
        "date": "2026-03-24",
        "role": "sales",
        "proficiency_level": "intermediate",
        "intro_message": "Today's focus is on communication excellence in sales.",
        "paragraph": "Building strong client relationships requires clear and persuasive communication. Successful sales professionals articulate their value proposition with conviction and adapt their messaging to resonate with diverse audiences. Effective communication transcends mere information delivery; it builds trust and demonstrates genuine understanding of client needs.",
        "vocabulary": [
            {"word": "articulate", "meaning": "To express ideas clearly and effectively", "usage_example": "The sales director articulated the new company strategy during the quarterly meeting.", "pronunciation": "ar-TIK-yuh-layt"},
            {"word": "conviction", "meaning": "A strong belief or firm opinion", "usage_example": "She spoke with conviction about the product's benefits.", "pronunciation": "kun-VIK-shun"},
            {"word": "resonate", "meaning": "To strike a chord; to have widespread influence", "usage_example": "The company's mission statement resonates with employees across all departments.", "pronunciation": "REZ-uh-nayt"},
            {"word": "transcend", "meaning": "To go beyond the limits of something", "usage_example": "Great leaders transcend conventional thinking to drive innovation.", "pronunciation": "tran-SEND"},
            {"word": "proposition", "meaning": "A suggested plan or offer", "usage_example": "The consultant presented a compelling value proposition to attract new clients.", "pronunciation": "prah-puh-ZISH-un"},
            {"word": "diverse", "meaning": "Showing great variety; different from each other", "usage_example": "Our diverse team brings different perspectives to problem-solving.", "pronunciation": "duh-VERS"},
            {"word": "leverage", "meaning": "To use something to maximum advantage", "usage_example": "We leveraged our existing relationships to expand into new markets.", "pronunciation": "LEV-er-ij"},
            {"word": "rapport", "meaning": "A relationship of understanding and harmony", "usage_example": "Building rapport with clients is essential for long-term business relationships.", "pronunciation": "ruh-POR"},
            {"word": "strategic", "meaning": "Carefully planned and designed", "usage_example": "The strategic partnership created mutual benefits for both organizations.", "pronunciation": "struh-TEE-jik"},
            {"word": "initiative", "meaning": "The ability to take action independently; a new plan or program", "usage_example": "She took the initiative to lead the customer retention program.", "pronunciation": "ih-NISH-uh-tiv"},
            {"word": "advocate", "meaning": "To publicly recommend or support", "usage_example": "We advocate for customer-centric policies in all our business decisions.", "pronunciation": "AD-vuh-kayt"},
            {"word": "facilitate", "meaning": "To make something easier or more possible", "usage_example": "Clear communication facilitates better understanding between departments.", "pronunciation": "fuh-SIL-uh-tayt"}
        ]
    }"""


def test_agent_initialization_success(mock_google_api_key: str) -> None:
    """Test successful initialization of DailyLearningAgent."""
    with patch("commucraft_ai.agent.daily_learning_agent.ChatGoogleGenerativeAI"):
        agent = DailyLearningAgent(google_api_key=mock_google_api_key)
        assert agent.google_api_key == mock_google_api_key
        assert agent.llm is not None
        assert agent.prompt_template is not None


def test_agent_initialization_empty_key() -> None:
    """Test that empty API key raises ValueError."""
    with pytest.raises(ValueError, match="cannot be empty"):
        DailyLearningAgent(google_api_key="")


def test_agent_initialization_none_key() -> None:
    """Test that None API key raises ValueError."""
    with pytest.raises(ValueError, match="cannot be empty"):
        DailyLearningAgent(google_api_key=None)  # type: ignore


@patch("commucraft_ai.agent.daily_learning_agent.ChatGoogleGenerativeAI")
@patch("commucraft_ai.agent.daily_learning_agent.ChatPromptTemplate")
def test_generate_daily_content_success(
    mock_prompt_class: MagicMock,
    mock_llm_class: MagicMock,
    mock_google_api_key: str,
    sample_llm_response: str,
) -> None:
    """Test successful generation of daily learning content."""
    # Setup mock LLM
    mock_llm = MagicMock()
    mock_llm_class.return_value = mock_llm

    # Setup mock prompt template
    mock_prompt = MagicMock()
    mock_prompt_class.from_messages.return_value = mock_prompt

    # Mock the chain response
    mock_response = MagicMock()
    mock_response.content = sample_llm_response

    mock_chain = MagicMock()
    mock_chain.invoke.return_value = mock_response
    mock_prompt.__or__.return_value = mock_chain

    agent = DailyLearningAgent(google_api_key=mock_google_api_key)

    # Generate content
    content = agent.generate_daily_content(role="sales", proficiency_level="intermediate")

    # Verify response structure
    assert content["date"] == "2026-03-24"
    assert content["role"] == "sales"
    assert content["proficiency_level"] == "intermediate"
    assert "paragraph" in content
    assert len(content["paragraph"]) > 0
    assert "vocabulary" in content
    assert 10 <= len(content["vocabulary"]) <= 20


@patch("commucraft_ai.agent.daily_learning_agent.ChatGoogleGenerativeAI")
@patch("commucraft_ai.agent.daily_learning_agent.ChatPromptTemplate")
def test_generate_daily_content_vocabulary_validation(
    mock_prompt_class: MagicMock,
    mock_llm_class: MagicMock,
    mock_google_api_key: str,
    sample_llm_response: str,
) -> None:
    """Test that generated vocabulary has all required fields."""
    mock_llm = MagicMock()
    mock_llm_class.return_value = mock_llm

    mock_prompt = MagicMock()
    mock_prompt_class.from_messages.return_value = mock_prompt

    mock_response = MagicMock()
    mock_response.content = sample_llm_response

    mock_chain = MagicMock()
    mock_chain.invoke.return_value = mock_response
    mock_prompt.__or__.return_value = mock_chain

    agent = DailyLearningAgent(google_api_key=mock_google_api_key)
    content = agent.generate_daily_content(role="sales", proficiency_level="intermediate")

    # Verify each word has required fields
    required_fields = ["word", "meaning", "usage_example", "pronunciation"]
    for word_entry in content["vocabulary"]:
        for field in required_fields:
            assert field in word_entry
            assert isinstance(word_entry[field], str)
            assert len(word_entry[field]) > 0


@patch("commucraft_ai.agent.daily_learning_agent.ChatGoogleGenerativeAI")
@patch("commucraft_ai.agent.daily_learning_agent.ChatPromptTemplate")
def test_generate_daily_content_invalid_json(
    mock_prompt_class: MagicMock,
    mock_llm_class: MagicMock,
    mock_google_api_key: str,
) -> None:
    """Test that invalid JSON response raises ValueError."""
    mock_llm = MagicMock()
    mock_llm_class.return_value = mock_llm

    mock_prompt = MagicMock()
    mock_prompt_class.from_messages.return_value = mock_prompt

    mock_response = MagicMock()
    mock_response.content = "This is not valid JSON"

    mock_chain = MagicMock()
    mock_chain.invoke.return_value = mock_response
    mock_prompt.__or__.return_value = mock_chain

    agent = DailyLearningAgent(google_api_key=mock_google_api_key)

    with pytest.raises(ValueError, match="No JSON|not valid JSON"):
        agent.generate_daily_content(role="sales", proficiency_level="intermediate")


@patch("commucraft_ai.agent.daily_learning_agent.ChatGoogleGenerativeAI")
@patch("commucraft_ai.agent.daily_learning_agent.ChatPromptTemplate")
def test_generate_daily_content_retry_on_failure(
    mock_prompt_class: MagicMock,
    mock_llm_class: MagicMock,
    mock_google_api_key: str,
    sample_llm_response: str,
) -> None:
    """Test that agent retries on API failure."""
    mock_llm = MagicMock()
    mock_llm_class.return_value = mock_llm

    mock_prompt = MagicMock()
    mock_prompt_class.from_messages.return_value = mock_prompt

    # First call fails, second succeeds
    mock_response = MagicMock()
    mock_response.content = sample_llm_response

    mock_chain = MagicMock()
    side_effects = [Exception("API Error"), mock_response]
    mock_chain.invoke.side_effect = side_effects
    mock_prompt.__or__.return_value = mock_chain

    agent = DailyLearningAgent(google_api_key=mock_google_api_key)

    # Should succeed due to retry logic
    content = agent.generate_daily_content(role="sales", proficiency_level="intermediate")
    assert content["role"] == "sales"
