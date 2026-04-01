"""Memory system using semantic similarity to avoid repeating responses.

This module handles searching through previous responses and finding similar
questions to provide context and avoid repetition.
"""

from sentence_transformers import SentenceTransformer, util

from commucraft_ai.utils.logger import get_logger

logger = get_logger("memory_system")


class MemorySystem:
    """Manages semantic search through previous Q&A responses."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2") -> None:
        """
        Initialize the memory system with a semantic embedding model.

        Args:
            model_name (str): Name of the sentence-transformers model to use.
                              Defaults to 'all-MiniLM-L6-v2' (fast and efficient).

        Errors:
            Exception: If model loading fails.
        """
        try:
            self.model = SentenceTransformer(model_name)
            logger.info(f"Memory system initialized with model: {model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize memory system: {str(e)}")
            raise

    def find_similar_responses(
        self, query: str, all_responses: list[dict], top_k: int = 3, similarity_threshold: float = 0.5
    ) -> list[dict]:
        """
        Find similar previous responses to a given query.

        Uses semantic similarity to find relevant Q&As from history. Returns only
        responses above the similarity threshold.

        Args:
            query (str): The user's current query
            all_responses (list[dict]): List of previous Q&A dicts with 'question' and 'answer' keys
            top_k (int): Maximum number of similar responses to return. Defaults to 3.
            similarity_threshold (float): Only return responses with similarity >= this value. Defaults to 0.5.

        Returns:
            list[dict]: List of similar response dicts sorted by similarity (highest first)

        Errors:
            ValueError: If query is empty or all_responses is invalid.

        Example:
            Input: find_similar_responses("How to write emails?", [...], top_k=3)
            Output: [{"question": "...", "answer": "...", "similarity": 0.87}, ...]
        """
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")

        if not all_responses or not isinstance(all_responses, list):
            logger.warning("No previous responses to search through")
            return []

        try:
            # Encode the current query
            query_embedding = self.model.encode(query, convert_to_tensor=True)

            similarities = []

            # Calculate similarity for each previous response's question
            for response in all_responses:
                if "question" not in response:
                    logger.warning("Response missing 'question' field, skipping")
                    continue

                previous_question = response.get("question", "")
                if not previous_question:
                    continue

                # Encode and compare
                prev_embedding = self.model.encode(previous_question, convert_to_tensor=True)
                similarity_score = util.pytorch_cos_sim(query_embedding, prev_embedding).item()

                if similarity_score >= similarity_threshold:
                    similarities.append(
                        {
                            "question": response["question"],
                            "answer": response.get("answer", ""),
                            "similarity": similarity_score,
                        }
                    )

            # Sort by similarity (highest first) and return top_k
            similarities.sort(key=lambda x: x["similarity"], reverse=True)
            result = similarities[:top_k]

            logger.info(f"Found {len(result)} similar responses to query")
            return result

        except Exception as e:
            logger.error(f"Error finding similar responses: {str(e)}")
            return []

    def extract_qa_from_content(self, html_content: str) -> list[dict]:
        """
        Extract Q&A pairs from Confluence HTML content.

        Parses stored Q&A content and extracts question-answer pairs.
        Assumes content is formatted with timestamps and Q&A blocks.

        Args:
            html_content (str): HTML content from Confluence page

        Returns:
            list[dict]: List of Q&A dicts with 'question', 'answer', and 'timestamp' keys

        Errors:
            ValueError: If html_content is empty.
            Exception: If parsing fails.

        Example:
            Input: extract_qa_from_content("<p>[2024-01-01 10:00] Q: ...A: ...</p>")
            Output: [{"question": "...", "answer": "...", "timestamp": "2024-01-01 10:00"}]
        """
        if not html_content or not isinstance(html_content, str):
            raise ValueError("HTML content must be a non-empty string")

        try:
            import re

            # Remove HTML tags
            text_content = re.sub(r"<[^>]+>", "", html_content)

            # Pattern to match Q&A blocks: [timestamp] Q: question A: answer
            qa_pattern = r"\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\].*?Q:\s*(.*?)\s*A:\s*(.*?)(?=\[|$)"

            matches = re.findall(qa_pattern, text_content, re.DOTALL)

            qa_pairs = [
                {"timestamp": match[0], "question": match[1].strip(), "answer": match[2].strip()}
                for match in matches
                if match[1].strip() and match[2].strip()
            ]

            logger.info(f"Extracted {len(qa_pairs)} Q&A pairs from content")
            return qa_pairs

        except Exception as e:
            logger.error(f"Error extracting Q&A pairs: {str(e)}")
            return []

    def format_context_for_llm(self, similar_responses: list[dict], max_tokens: int = 500) -> str:
        """
        Format similar responses as context for the LLM.

        Creates a formatted string of similar responses to include in the LLM prompt,
        helping it understand context and avoid repetition.

        Args:
            similar_responses (list[dict]): List of similar response dicts
            max_tokens (int): Maximum token length for the context. Defaults to 500 (rough estimate).

        Returns:
            str: Formatted context string for inclusion in LLM prompt

        Example:
            Input: format_context_for_llm([{"question": "...", "answer": "..."}])
            Output: "Previous similar responses:\\n1. Q: ...\\nA: ...\\n\\n2. Q: ..."
        """
        if not similar_responses:
            return ""

        try:
            context_lines = ["## Previous Similar Responses (for context and avoiding repetition):"]

            token_count = 0
            for idx, response in enumerate(similar_responses, 1):
                question = response.get("question", "")
                answer = response.get("answer", "")
                similarity = response.get("similarity", 0)

                # Rough estimate: 1 token ≈ 4 characters
                estimated_tokens = (len(question) + len(answer)) // 4

                if token_count + estimated_tokens > max_tokens:
                    context_lines.append("\n(... truncated for token limit)")
                    break

                context_lines.append(f"\n**Q{idx}** (similarity: {similarity:.2%}): {question}")
                context_lines.append(f"**A{idx}**: {answer[:200]}..." if len(answer) > 200 else f"**A{idx}**: {answer}")

                token_count += estimated_tokens

            return "\n".join(context_lines)

        except Exception as e:
            logger.error(f"Error formatting context: {str(e)}")
            return ""
