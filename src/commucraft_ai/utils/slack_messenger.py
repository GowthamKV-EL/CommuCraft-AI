"""Slack messenger for posting daily learning content to Slack channels.

This module handles sending formatted daily learning content to Slack
through the Bot User OAuth Token authentication method.
"""

import os
from typing import Optional

from commucraft_ai.utils.logger import get_logger

logger = get_logger("slack_messenger")


class SlackMessenger:
    """
    Sends daily learning content to Slack channels.

    Handles authentication and message posting to Slack. Requires:
    - SLACK_BOT_TOKEN: Bot User OAuth Token (from Slack app settings)
    - SLACK_CHANNEL_ID: Channel ID where messages should be posted
    """

    def __init__(self, bot_token: Optional[str] = None, channel_id: Optional[str] = None) -> None:
        """
        Initialize Slack messenger with authentication credentials.

        Args:
            bot_token (Optional[str]): Slack Bot User OAuth Token. If None, attempts to load from env.
            channel_id (Optional[str]): Slack channel ID. If None, attempts to load from env.

        Errors:
            ValueError: If required credentials are missing or invalid.
        """
        self.bot_token = bot_token or os.getenv("SLACK_BOT_TOKEN")
        self.channel_id = channel_id or os.getenv("SLACK_CHANNEL_ID")
        self.thread_ts = os.getenv("SLACK_THREAD_TS")  # Optional: specific thread ID

        if not self.bot_token:
            raise ValueError(
                "SLACK_BOT_TOKEN not provided. Set it as parameter or SLACK_BOT_TOKEN environment variable."
            )

        if not self.channel_id:
            raise ValueError(
                "SLACK_CHANNEL_ID not provided. Set it as parameter or SLACK_CHANNEL_ID environment variable."
            )

        logger.debug("Slack messenger initialized with channel: %s", self.channel_id)

    def send_message(self, markdown_content: str) -> dict:
        """
        Send markdown-formatted message to Slack.

        Posts the provided markdown content to the configured Slack channel.
        Uses mrkdwn format for proper markdown rendering.

        Args:
            markdown_content (str): Markdown-formatted message to send.

        Returns:
            dict: Slack API response containing message timestamp and other metadata.

        Errors:
            ImportError: If slack_sdk is not installed.
            Exception: If Slack API call fails.

        Example:
            Input: markdown_content = "# Welcome\n\nYour daily content here..."
            Output: {"ok": true, "channel": "C123456", "ts": "1234567890.123456", ...}
        """
        try:
            from slack_sdk import WebClient
            from slack_sdk.errors import SlackApiError
        except ImportError:
            raise ImportError("slack-sdk is not installed. Install it with: uv add slack-sdk")

        try:
            client = WebClient(token=self.bot_token)

            # Prepare message payload
            payload = {
                "channel": self.channel_id,
                "text": markdown_content,  # Fallback text
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": markdown_content,
                        },
                    }
                ],
            }

            # If thread_ts is set, post as reply to thread
            if self.thread_ts:
                payload["thread_ts"] = self.thread_ts
                logger.debug("Posting message to thread: %s", self.thread_ts)

            # Send message
            response = client.chat_postMessage(**payload)

            logger.info(
                "Message posted to Slack successfully. Channel: %s, Timestamp: %s",
                response["channel"],
                response["ts"],
            )

            return response

        except SlackApiError as e:
            logger.error(
                "Slack API error: %s (Error Code: %s)",
                str(e),
                e.response.get("error") if hasattr(e, "response") else "Unknown",
            )
            raise Exception(f"Failed to post message to Slack: {str(e)}")

        except Exception as e:
            logger.error("Unexpected error posting to Slack: %s", str(e))
            raise


def send_daily_content_to_slack(markdown_content: str) -> bool:
    """
    Convenience function to send daily content to Slack.

    Loads credentials from environment and sends the formatted content.

    Args:
        markdown_content (str): Markdown-formatted daily content.

    Returns:
        bool: True if message was posted successfully, False otherwise.

    Errors:
        ValueError: If Slack credentials are not configured.

    Example:
        Input: send_daily_content_to_slack("# Welcome\n\nDaily content...")
        Output: True (if successful)
    """
    try:
        slack_enabled = os.getenv("SLACK_ENABLED", "false").lower() == "true"

        if not slack_enabled:
            logger.debug("Slack integration is disabled (SLACK_ENABLED=false)")
            return False

        messenger = SlackMessenger()
        response = messenger.send_message(markdown_content)
        return response.get("ok", False)

    except ValueError as e:
        logger.warning("Slack messenger not configured: %s", str(e))
        return False
    except Exception as e:
        logger.error("Failed to send content to Slack: %s", str(e))
        return False
