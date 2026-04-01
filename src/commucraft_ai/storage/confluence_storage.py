"""Confluence integration for document storage and retrieval.

This module handles all Confluence operations including creating pages,
appending content, and retrieving previous responses for memory.
"""

from datetime import datetime
from typing import Optional

from atlassian import Confluence

from commucraft_ai.utils.logger import get_logger

logger = get_logger("confluence_storage")


class ConfluenceStorage:
    """Manages document storage and retrieval in Confluence."""

    def __init__(
        self,
        confluence_url: str,
        confluence_username: str,
        confluence_api_token: str,
        confluence_space: str,
    ) -> None:
        """
        Initialize Confluence storage client.

        Args:
            confluence_url (str): Confluence instance URL (e.g., https://company.atlassian.net/wiki)
            confluence_username (str): Confluence username or email
            confluence_api_token (str): Confluence API token for authentication
            confluence_space (str): Confluence space key where pages will be stored

        Errors:
            ValueError: If any required parameters are empty or invalid.
            Exception: If Confluence connection fails.
        """
        if not all([confluence_url, confluence_username, confluence_api_token, confluence_space]):
            raise ValueError("All Confluence parameters must be provided and non-empty")

        self.confluence_url = confluence_url
        self.confluence_username = confluence_username
        self.confluence_api_token = confluence_api_token
        self.confluence_space = confluence_space

        try:
            self.confluence = Confluence(
                url=confluence_url,
                username=confluence_username,
                password=confluence_api_token,
            )
            logger.info("Confluence client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Confluence client: {str(e)}")
            raise

    def get_or_create_page(self, page_title: str) -> Optional[dict]:
        """
        Get an existing page or create a new one if it doesn't exist.

        Args:
            page_title (str): Title of the page to get or create

        Returns:
            Optional[dict]: Page info dict with 'id' and 'body' keys, or None if creation fails

        Errors:
            ValueError: If page_title is empty.
            Exception: If Confluence API call fails.
        """
        if not page_title or not page_title.strip():
            raise ValueError("Page title cannot be empty")

        try:
            # Try to find existing page
            pages = self.confluence.get_page_by_title(self.confluence_space, page_title)
            if pages:
                logger.info(f"Found existing page: {page_title}")
                return pages
            else:
                logger.info(f"Page not found, creating new page: {page_title}")
                return self._create_new_page(page_title)
        except Exception as e:
            logger.warning(f"Error searching for page: {str(e)}, attempting to create")
            return self._create_new_page(page_title)

    def _create_new_page(self, page_title: str) -> Optional[dict]:
        """
        Create a new Confluence page.

        Args:
            page_title (str): Title of the new page

        Returns:
            Optional[dict]: Page info dict or None if creation fails

        Errors:
            Exception: If page creation fails.
        """
        try:
            initial_content = f"<p><em>Page created on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</em></p>"
            page = self.confluence.create_page(
                space=self.confluence_space,
                title=page_title,
                body=initial_content,
            )
            logger.info(f"Created new page: {page_title} (ID: {page.get('id') if page else 'unknown'})")
            return page
        except Exception as e:
            logger.error(f"Failed to create new page: {str(e)}")
            return None

    def append_to_page(self, page_title: str, content: str, section_title: Optional[str] = None) -> bool:
        """
        Append content to a Confluence page.

        Args:
            page_title (str): Title of the page to append to
            content (str): HTML content to append
            section_title (str, optional): Optional section title to organize content

        Returns:
            bool: True if append succeeded, False otherwise

        Errors:
            ValueError: If page_title or content is empty.
            Exception: If Confluence API call fails.
        """
        if not page_title or not content:
            raise ValueError("Page title and content cannot be empty")

        try:
            page = self.get_or_create_page(page_title)
            if not page or "id" not in page:
                logger.error("Could not retrieve or create page for appending")
                return False

            page_id = page["id"]
            body_dict = page.get("body") or {}
            storage_dict = body_dict.get("storage") or {}
            current_body = storage_dict.get("value", "")

            # Format new content with timestamp and optional section title
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            formatted_content = f"<p><strong>[{timestamp}]</strong>"
            if section_title:
                formatted_content += f" <em>{section_title}</em>"
            formatted_content += f"</p>{content}"

            # Append to existing content
            new_body = current_body + formatted_content

            # Update the page
            self.confluence.update_page(
                page_id=page_id,
                title=page_title,
                body=new_body,
            )
            logger.info(f"Successfully appended content to page: {page_title}")
            return True

        except Exception as e:
            logger.error(f"Failed to append to page: {str(e)}")
            return False

    def get_page_content(self, page_title: str) -> Optional[str]:
        """
        Retrieve the full content of a Confluence page.

        Args:
            page_title (str): Title of the page to retrieve

        Returns:
            Optional[str]: Page content as HTML string, or None if retrieval fails

        Errors:
            ValueError: If page_title is empty.
            Exception: If Confluence API call fails.
        """
        if not page_title or not page_title.strip():
            raise ValueError("Page title cannot be empty")

        try:
            page = self.get_or_create_page(page_title)
            if not page:
                logger.warning(f"Could not retrieve page: {page_title}")
                return None

            content = page.get("body", {}).get("storage", {}).get("value", "")
            logger.info(f"Retrieved content from page: {page_title}")
            return content

        except Exception as e:
            logger.error(f"Failed to retrieve page content: {str(e)}")
            return None

    def search_in_page(self, page_title: str, search_term: str) -> list[str]:
        """
        Search for a term in a specific page and return matching snippets.

        Args:
            page_title (str): Title of the page to search in
            search_term (str): Term to search for

        Returns:
            list[str]: List of matching snippets (text portions containing the search term)

        Errors:
            ValueError: If page_title or search_term is empty.
            Exception: If Confluence API call fails.
        """
        if not page_title or not search_term:
            raise ValueError("Page title and search term cannot be empty")

        try:
            content = self.get_page_content(page_title)
            if not content:
                logger.warning(f"Could not retrieve content for search: {page_title}")
                return []

            # Basic text extraction and search (in production, use proper HTML parsing)
            import re

            # Remove HTML tags for searching
            text_content = re.sub(r"<[^>]+>", "", content)

            # Find all sentences/snippets containing the search term
            sentences = re.split(r"[.!?]+", text_content)
            matching_snippets = [s.strip() for s in sentences if search_term.lower() in s.lower() and s.strip()]

            logger.info(f"Found {len(matching_snippets)} matching snippets for '{search_term}'")
            return matching_snippets

        except Exception as e:
            logger.error(f"Failed to search in page: {str(e)}")
            return []
