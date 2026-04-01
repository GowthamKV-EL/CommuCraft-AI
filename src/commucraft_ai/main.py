"""Main entry point for CommuCraft-AI learning agent with multiple modes.

This module supports three operational modes:
1. --now: Run immediately and exit (saves to Confluence)
2. --schedule: Background daemon mode (generates daily at 2 PM IST, non-blocking)
3. --chat: Interactive chat mode with semantic memory and optional save

The scheduler runs as a background process that doesn't block the CLI.
Chat responses can be optionally saved to Confluence with user permission.
"""

import argparse
import signal
import sys
import threading
import time
from datetime import datetime
from typing import Any, Optional

from apscheduler.schedulers.background import BackgroundScheduler

from commucraft_ai.agent.daily_learning_agent import DailyLearningAgent
from commucraft_ai.agent.query_agent import QueryAgent
from commucraft_ai.config import Config, load_config
from commucraft_ai.storage.confluence_storage import ConfluenceStorage
from commucraft_ai.storage.daily_storage import save_daily_content
from commucraft_ai.storage.memory_system import MemorySystem
from commucraft_ai.utils.logger import setup_logger
from commucraft_ai.utils.markdown_formatter import format_daily_content_to_markdown
from commucraft_ai.utils.slack_messenger import send_daily_content_to_slack

# Initialize logger at module level for use in signal handlers
logger = setup_logger()

# Constants for Confluence page names
DAILY_CONTENT_PAGE_TITLE = "CommuCraft Daily Learning Content"
CHAT_QA_PAGE_TITLE = "CommuCraft Chat Q&A Memory"

# Global scheduler reference for signal handling (protected by lock)
_scheduler: Optional[BackgroundScheduler] = None
_scheduler_lock = threading.Lock()


def initialize_confluence_storage(config: Config) -> Optional[ConfluenceStorage]:
    """
    Initialize Confluence storage if credentials are configured.

    Args:
        config (Config): Configuration object with Confluence settings.

    Returns:
        Optional[ConfluenceStorage]: Initialized Confluence storage or None if not configured.
    """
    if not all([config.confluence_url, config.confluence_username, config.confluence_api_token]):
        logger.warning("Confluence credentials not configured. Memory features will be disabled.")
        return None

    try:
        return ConfluenceStorage(
            confluence_url=config.confluence_url or "",
            confluence_username=config.confluence_username or "",
            confluence_api_token=config.confluence_api_token or "",
            confluence_space=config.confluence_space or "COMMUCRAFT",
        )
    except Exception as e:
        logger.warning(f"Failed to initialize Confluence storage: {str(e)}. Continuing without memory.")
        return None


def run_daily_job(agent: DailyLearningAgent, config: Config, confluence_storage: Optional[ConfluenceStorage]) -> None:
    """
    Execute the daily learning content generation job.

    Generates content, saves it to JSON and Confluence, formats it to markdown,
    and optionally sends it to Slack if configured.

    Args:
        agent (DailyLearningAgent): Initialized daily learning agent.
        config (Config): Configuration object with user settings.
        confluence_storage (ConfluenceStorage, optional): Confluence storage for appending content.

    Returns:
        None

    Errors:
        All exceptions are caught and logged. No exceptions are raised to the caller.
    """
    logger.info("=" * 60)
    logger.info("Starting daily learning job")
    logger.info("=" * 60)

    try:
        # Generate daily content
        logger.info(f"Generating content for role: {config.role}, level: {config.proficiency_level}")
        content = agent.generate_daily_content(role=config.role, proficiency_level=config.proficiency_level)

        # Save content to JSON
        file_path = save_daily_content(content)

        logger.info(f"✓ Daily content successfully generated and saved to {file_path}")
        logger.info(f"✓ Generated {len(content['vocabulary'])} vocabulary words")
        logger.info(f"✓ Paragraph length: {len(content['paragraph'].split())} words")

        # Format content to markdown
        try:
            markdown_content = format_daily_content_to_markdown(content)
            logger.debug("✓ Content formatted to markdown")
        except Exception as e:
            logger.error(f"Failed to format content to markdown: {str(e)}")
            raise

        # Append to Confluence if available
        if confluence_storage:
            try:
                formatted_html = (
                    f"<h3>📚 {content.get('intro_message', 'Daily Learning')}</h3>"
                    f"<p><strong>Paragraph:</strong> {content.get('paragraph', '')}</p>"
                    f"<p><strong>Vocabulary:</strong></p><ul>"
                )
                for word_obj in content.get("vocabulary", []):
                    if isinstance(word_obj, dict):
                        formatted_html += (
                            f"<li><strong>{word_obj.get('word')}</strong>: "
                            f"{word_obj.get('meaning')} ({word_obj.get('phonetic')})</li>"
                        )
                formatted_html += "</ul>"

                confluence_storage.append_to_page(
                    DAILY_CONTENT_PAGE_TITLE, formatted_html, section_title="Daily Content"
                )
                logger.info("✓ Content appended to Confluence")
            except Exception as e:
                logger.warning(f"Failed to append to Confluence: {str(e)} (continuing anyway)")

        # Attempt to send to Slack if enabled
        try:
            slack_sent = send_daily_content_to_slack(markdown_content)
            if slack_sent:
                logger.info("✓ Daily content successfully sent to Slack")
            else:
                logger.debug("Slack integration is disabled (not configured)")
        except Exception as e:
            logger.warning(f"Failed to send to Slack (continuing anyway): {str(e)}")

    except Exception as e:
        logger.error(f"✗ Failed to generate daily content: {str(e)}", exc_info=True)


def signal_handler(sig: int, frame: Any) -> None:
    """
    Handle interrupt signals gracefully with thread-safe scheduler shutdown.

    Args:
        sig (int): Signal number.
        frame (Any): Current stack frame.

    Returns:
        None
    """
    logger.info("Interrupt signal received. Shutting down gracefully...")
    with _scheduler_lock:
        if _scheduler:
            _scheduler.shutdown()
    sys.exit(0)


def run_immediate_mode(config: Config) -> None:
    """
    Run the daily job immediately and exit.

    Args:
        config (Config): Configuration object with user settings.

    Returns:
        None
    """
    logger.info("Running in immediate mode (--now)")
    try:
        agent = DailyLearningAgent(google_api_key=config.google_api_key)  # type: ignore
        confluence_storage = initialize_confluence_storage(config)
        run_daily_job(agent, config, confluence_storage)
        logger.info("✓ Immediate run completed successfully. Exiting.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"✗ Immediate run failed: {str(e)}", exc_info=True)
        sys.exit(1)


def run_schedule_mode(config: Config) -> None:
    """
    Start the scheduler for daily runs at 2 PM IST (background mode, non-blocking).

    The scheduler runs independently and doesn't block the CLI.

    Args:
        config (Config): Configuration object with user settings.

    Returns:
        None
    """
    global _scheduler

    logger.info("Running in schedule mode (--schedule)")
    logger.info("Scheduling daily job at 14:00 IST (2 PM)")
    logger.info("The scheduler will save content to Confluence and optionally to Slack")

    try:
        # Initialize agent and storage
        agent = DailyLearningAgent(google_api_key=config.google_api_key)  # type: ignore
        confluence_storage = initialize_confluence_storage(config)

        # Initialize scheduler with IST timezone
        logger.info("Setting up APScheduler...")
        with _scheduler_lock:
            global _scheduler
            _scheduler = BackgroundScheduler(timezone="Asia/Kolkata")

        # Schedule the daily job at 2 PM IST
        with _scheduler_lock:
            _scheduler.add_job(
                run_daily_job,
                "cron",
                hour=14,
                minute=0,
                args=[agent, config, confluence_storage],
                id="daily_learning_job",
                name="Daily Learning Content Generation",
                timezone="Asia/Kolkata",
            )

        # Register signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        # Start scheduler
        logger.info("Starting scheduler...")
        with _scheduler_lock:
            _scheduler.start()

        # Get job with null check
        job = _scheduler.get_job("daily_learning_job")
        next_run = job.next_run_time if job else None
        if next_run:
            logger.info(f"✓ Scheduler started. Next run: {next_run}")
        else:
            logger.info("✓ Scheduler started.")
        logger.info("Scheduler is running. Press Ctrl+C to stop.")

        # Keep the scheduler running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received")
            _scheduler.shutdown()

    except Exception as e:
        logger.error(f"✗ Schedule mode failed: {str(e)}", exc_info=True)
        sys.exit(1)


def run_chat_mode(config: Config) -> None:
    """
    Start interactive chat mode for querying the agent with semantic memory.

    Allows users to type questions and receive instant responses. Responses can
    optionally be saved to Confluence. Maintains memory of previous Q&As to avoid repetition.

    Args:
        config (Config): Configuration object with user settings.

    Returns:
        None
    """
    logger.info("Running in chat mode (--chat)")

    try:
        # Initialize storage and memory
        confluence_storage = initialize_confluence_storage(config)
        memory_system = MemorySystem()

        # Initialize query agent
        logger.info("Initializing Query Agent with semantic memory...")
        query_agent = QueryAgent(
            google_api_key=config.google_api_key,  # type: ignore
            confluence_storage=confluence_storage,
            memory_system=memory_system,
        )

        logger.info("✓ Chat mode started. Type your questions (type 'quit' or 'exit' to stop)")
        logger.info("-" * 60)

        # Chat loop
        while True:
            try:
                # Get user input
                user_query = input("\nYou: ").strip()

                # Check for exit commands
                if user_query.lower() in ("quit", "exit", "q"):
                    logger.info("Chat mode ended. Exiting.")
                    sys.exit(0)

                # Skip empty queries
                if not user_query:
                    logger.warning("Please enter a valid query.")
                    continue

                # Process query
                logger.debug(f"Processing query: {user_query}")
                response = query_agent.answer_query(user_query, chat_qa_page_title=CHAT_QA_PAGE_TITLE)

                # Display response
                print(f"\nAgent: {response}")
                print("-" * 60)

                # Ask if user wants to save
                save_prompt = input("\nSave this Q&A? (yes/no): ").strip().lower()
                if save_prompt in ("yes", "y"):
                    if confluence_storage:
                        try:
                            # Format Q&A for storage
                            qa_html = f"<p><strong>Q: {user_query}</strong></p><p><strong>A: {response}</strong></p>"
                            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            confluence_storage.append_to_page(
                                CHAT_QA_PAGE_TITLE,
                                qa_html,
                                section_title=f"Q&A saved at {timestamp}",
                            )
                            logger.info("✓ Q&A saved to Confluence")
                            print("✓ Q&A saved successfully")
                        except Exception as e:
                            logger.error(f"Failed to save Q&A: {str(e)}")
                            print(f"Failed to save: {str(e)}")
                    else:
                        print("⚠ Confluence not configured. Q&A not saved.")
                        logger.warning("User requested save but Confluence not available")

            except KeyboardInterrupt:
                logger.info("Chat interrupted by user. Exiting.")
                sys.exit(0)
            except Exception as e:
                logger.error(f"Error processing query: {str(e)}")
                print(f"Error: {str(e)}")
                continue

    except Exception as e:
        logger.error(f"✗ Chat mode failed: {str(e)}", exc_info=True)
        sys.exit(1)


def main(args: Optional[list[str]] = None) -> None:
    """
    Initialize and run CommuCraft-AI in the specified mode.

    Supports three modes:
    1. --now: Run daily job immediately and exit
    2. --schedule: Run scheduler for daily runs at 2 PM IST
    3. --chat: Start interactive chat mode

    Args:
        args (list[str] | None): Command-line arguments. If None, uses sys.argv[1:].

    Returns:
        None
    """
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="CommuCraft-AI Learning Agent with Confluence Memory")
    parser.add_argument(
        "--now",
        action="store_true",
        help="Run the daily job immediately and exit",
    )
    parser.add_argument(
        "--schedule",
        action="store_true",
        help="Start scheduler for daily runs at 2 PM IST",
    )
    parser.add_argument(
        "--chat",
        action="store_true",
        help="Start interactive chat mode to query the agent with semantic memory",
    )
    parsed_args = parser.parse_args(args)

    logger.info("CommuCraft-AI Learning Agent")
    logger.info("Starting initialization...")

    try:
        # Load configuration
        logger.info("Loading configuration...")
        config = load_config()
        logger.info(f"Configuration loaded: {config.to_dict()}")

        # Validate that google_api_key is set
        if not config.google_api_key:
            raise ValueError("GOOGLE_API_KEY is not set in environment. Please configure it in .env file.")

        # Determine which mode to run
        if parsed_args.now:
            run_immediate_mode(config)
        elif parsed_args.chat:
            run_chat_mode(config)
        else:
            # Default to schedule mode (--schedule or no mode specified)
            run_schedule_mode(config)

    except ValueError as e:
        logger.error(f"Configuration error: {str(e)}", exc_info=True)
        sys.exit(1)
    except FileNotFoundError as e:
        logger.error(f"Required file not found: {str(e)}", exc_info=True)
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
