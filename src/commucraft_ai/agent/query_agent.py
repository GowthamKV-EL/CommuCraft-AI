"""Query agent for interactive question-answering powered by Google Gemini API.

This module implements an interactive AI agent for answering user queries in real-time using google-genai.
It uses semantic memory to avoid repeating previous responses.
"""

from typing import Optional

import google.genai as genai

from commucraft_ai.storage.confluence_storage import ConfluenceStorage
from commucraft_ai.storage.memory_system import MemorySystem
from commucraft_ai.utils.logger import get_logger
from commucraft_ai.utils.retry_handler import retry_with_backoff

logger = get_logger("query_agent")

QUERY_SYSTEM_PROMPT = """You are a helpful, professional communication assistant for workplace learning.
You provide clear, concise, and practical answers to user queries about:
- Professional communication and writing
- Business English and vocabulary
- Communication strategies and techniques
- Professional development and learning

Maintain a friendly and supportive tone while being precise and informative.
Provide examples when relevant to help the user understand better.

IMPORTANT: If similar previous responses are provided in the context below, review them and:
1. Acknowledge the previous answer if your response is similar
2. Provide NEW perspectives, examples, or details not mentioned before
3. Avoid repeating the exact same information"""


class QueryAgent:
    """AI agent for answering user queries with semantic memory to avoid repetition."""

    def __init__(
        self,
        google_api_key: str,
        confluence_storage: Optional[ConfluenceStorage] = None,
        memory_system: Optional[MemorySystem] = None,
    ) -> None:
        """
        Initialize the query agent with Google Gemini LLM and optional memory.

        Args:
            google_api_key (str): Google API key for Gemini access.
            confluence_storage (ConfluenceStorage, optional): Confluence storage for memory. If None, memory features disabled.
            memory_system (MemorySystem, optional): Memory system for semantic search. If None, uses default.

        Errors:
            ValueError: If google_api_key is empty or invalid.
        """
        if not google_api_key:
            raise ValueError("google_api_key cannot be empty")

        self.google_api_key = google_api_key
        self.confluence_storage = confluence_storage
        self.memory_system = memory_system or MemorySystem()

        # Initialize google-genai client with API key
        self.client = genai.Client(api_key=google_api_key)

        logger.info("Query agent initialized successfully")

    @retry_with_backoff(max_retries=3, initial_delay=1.0)
    def answer_query(self, query: str, chat_qa_page_title: Optional[str] = None) -> str:
        """
        Answer a user query using the Gemini LLM with semantic memory context.

        Processes user questions, searches for similar previous responses to provide context,
        and generates informative responses with retry logic for API resilience.

        Args:
            query (str): The user's question or query.
            chat_qa_page_title (str, optional): Confluence page title for storing Q&As. If provided, searches for similar responses.

        Returns:
            str: The agent's response to the user's query.

        Errors:
            ValueError: If query is empty or invalid.
            Exception: If API call fails after 3 retry attempts.

        Example:
            Input: answer_query("What are effective ways to start a professional email?")
            Output: "An effective professional email should start with..."
        """
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")

        logger.info(f"Processing query: {query[:100]}")

        # Build context from memory if Confluence storage is available
        memory_context = ""
        if self.confluence_storage and chat_qa_page_title:
            try:
                logger.debug("Searching for similar previous responses...")
                page_content = self.confluence_storage.get_page_content(chat_qa_page_title)
                if page_content:
                    qa_pairs = self.memory_system.extract_qa_from_content(page_content)
                    if qa_pairs:
                        similar_responses = self.memory_system.find_similar_responses(query, qa_pairs, top_k=3)
                        if similar_responses:
                            memory_context = self.memory_system.format_context_for_llm(similar_responses)
                            logger.debug(f"Found {len(similar_responses)} similar responses for context")
            except Exception as e:
                logger.warning(f"Could not retrieve memory context: {str(e)} (continuing without memory)")

        # Build the full prompt
        full_prompt = f"{QUERY_SYSTEM_PROMPT}\n\n{memory_context}\n\nUser query: {query}"

        logger.debug("Invoking Gemini LLM for query processing...")

        # Use google-genai Client for chat
        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                {
                    "role": "user",
                    "parts": [
                        {
                            "text": full_prompt,
                        }
                    ],
                }
            ],
        )

        # Extract content from response
        response_text = response.text

        # Ensure response_text is a string
        if not isinstance(response_text, str):
            response_text = str(response_text)

        logger.debug(f"Received response from LLM: {len(response_text)} characters")

        return response_text
