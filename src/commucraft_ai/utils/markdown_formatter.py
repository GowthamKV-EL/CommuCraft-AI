"""Markdown formatter for daily learning content to Slack-ready format.

This module converts raw daily learning content to beautifully formatted markdown
suitable for posting to Slack or other messaging platforms.
"""

from typing import Any, Dict, List


def format_daily_content_to_markdown(content: Dict[str, Any]) -> str:
    """
    Convert daily learning content to markdown format.

    Takes the raw daily content dictionary and formats it as a structured markdown
    string with proper headers, emphasis, and spacing for Slack display.

    Args:
        content (Dict[str, Any]): Daily content dictionary containing:
            - intro_message: Personalized introduction
            - paragraph: Main learning paragraph
            - vocabulary: List of vocabulary items
            - role: User's role
            - proficiency_level: User's proficiency level

    Returns:
        str: Formatted markdown string ready for Slack posting.

    Errors:
        KeyError: If required fields are missing from content dictionary.
        ValueError: If content structure is invalid.

    Example:
        Input: {
            "intro_message": "As a sales professional...",
            "paragraph": "Effective communication is...",
            "vocabulary": [...],
            "role": "sales",
            "proficiency_level": "intermediate"
        }
        Output: Formatted markdown with headers, vocabulary table, etc.
    """
    try:
        # Validate required fields
        required_fields = ["intro_message", "paragraph", "vocabulary", "role", "proficiency_level"]
        for field in required_fields:
            if field not in content:
                raise KeyError(f"Missing required field in content: {field}")

        # Start building markdown
        markdown = []

        # Welcome header
        markdown.append("# 🎯 Welcome to Your Daily CommuCraft Session\n")

        # Personalized intro
        markdown.append(f"{content['intro_message']}\n")

        # Add role and proficiency level info
        markdown.append(f"*Role: {content['role'].title()} | Level: {content['proficiency_level'].title()}*\n")

        # Daily learning paragraph section
        markdown.append("## 📚 Daily Learning Paragraph\n")
        markdown.append(f"{content['paragraph']}\n")

        # Vocabulary builder section
        markdown.append("## 📖 Vocabulary Builder\n")
        markdown.append("*Enhance your professional vocabulary with these 15 essential words.*\n\n")

        # Format vocabulary as markdown table
        markdown.append("| Word | Meaning | Usage Example | Pronunciation |\n")
        markdown.append("|------|---------|---------------|----------------|\n")

        for vocab_item in content["vocabulary"]:
            # Escape pipe characters in fields to avoid markdown table issues
            word = vocab_item.get("word", "").replace("|", "\\|")
            meaning = vocab_item.get("meaning", "").replace("|", "\\|")
            usage = vocab_item.get("usage_example", "").replace("|", "\\|")
            pronunciation = vocab_item.get("pronunciation", "").replace("|", "\\|")

            # Truncate long fields for table readability
            if len(meaning) > 60:
                meaning = meaning[:57] + "..."
            if len(usage) > 60:
                usage = usage[:57] + "..."

            markdown.append(f"| {word} | {meaning} | {usage} | {pronunciation} |\n")

        markdown.append("\n")

        # Footer message
        markdown.append("*Keep practicing! Each day builds your professional communication excellence.*\n")

        return "".join(markdown)

    except KeyError as e:
        raise KeyError(f"Content validation failed: {str(e)}")
    except Exception as e:
        raise ValueError(f"Error formatting content to markdown: {str(e)}")


def format_vocabulary_for_slack(vocab_items: List[Dict[str, str]]) -> str:
    """
    Format vocabulary items as a detailed Slack-friendly list.

    Creates a multi-line formatted list with each word, meaning, usage, and pronunciation
    clearly separated for better readability in Slack.

    Args:
        vocab_items (list[Dict[str, str]]): List of vocabulary items, each containing:
            - word: The vocabulary word
            - meaning: Definition
            - usage_example: Usage in context
            - pronunciation: Phonetic pronunciation guide

    Returns:
        str: Formatted string with all vocabulary items.

    Errors:
        ValueError: If vocab_items is empty or items lack required fields.

    Example:
        Input: [{"word": "Paradigm", "meaning": "...", "usage_example": "...", "pronunciation": "..."}]
        Output: "1. Paradigm\n   📝 Definition: ...\n   💬 Usage: ...\n   🔊 Pronunciation: ...\n\n"
    """
    if not vocab_items:
        raise ValueError("Vocabulary list cannot be empty")

    formatted_vocab = []
    for idx, item in enumerate(vocab_items, 1):
        if not all(k in item for k in ["word", "meaning", "usage_example", "pronunciation"]):
            raise ValueError(f"Vocabulary item {idx} missing required fields")

        formatted_vocab.append(f"*{idx}. {item['word']}*")
        formatted_vocab.append(f"   📝 {item['meaning']}")
        formatted_vocab.append(f"   💬 {item['usage_example']}")
        formatted_vocab.append(f"   🔊 {item['pronunciation']}\n")

    return "\n".join(formatted_vocab)
