"""
Main entry point for CommuCraft-AI application.

This module initializes and runs the CommuCraft agent with daily task scheduling.
The application runs daily learning generation at the configured time and provides
an interface for users to interact with the communication coaching agent.

Args:
    None

Returns:
    None

Errors:
    Exception: If initialization or execution fails.
"""

import logging
import signal
import sys
import time
from typing import NoReturn

from src.sc_bot.agent.base_agent import CommuCraftAgent
from src.sc_bot.config import settings
from src.sc_bot.scheduler import TaskScheduler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("commucraft.log"),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger(__name__)


class CommuCraftApplication:
    """
    Main application class for CommuCraft-AI.

    This class manages the initialization of the agent, scheduler setup, and
    application lifecycle.

    Args:
        None

    Returns:
        None

    Errors:
        Exception: If initialization fails.
    """

    def __init__(self) -> None:
        """
        Initialize CommuCraft application.

        Args:
            None

        Returns:
            None

        Errors:
            Exception: If initialization fails.
        """
        try:
            logger.info("=" * 80)
            logger.info("Initializing CommuCraft-AI Application")
            logger.info("=" * 80)

            # Initialize agent
            self.agent = CommuCraftAgent()
            logger.info("✓ CommuCraft Agent initialized")

            # Initialize scheduler
            self.scheduler = TaskScheduler()
            logger.info("✓ Task Scheduler initialized")

            # Register signal handlers
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)

            logger.info("CommuCraft-AI Application ready")

        except Exception as e:
            logger.error(f"Failed to initialize application: {e}", exc_info=True)
            raise

    def _signal_handler(self, signum: int, frame: object) -> None:
        """
        Handle shutdown signals gracefully.

        Args:
            signum (int): Signal number.
            frame: Stack frame.

        Returns:
            None

        Errors:
            None
        """
        logger.info(f"Received signal {signum}. Shutting down gracefully...")
        self.shutdown()
        sys.exit(0)

    def setup_tasks(self) -> None:
        """
        Setup scheduled tasks for daily execution.

        Args:
            None

        Returns:
            None

        Errors:
            Exception: If task setup fails.

        Example:
            Input: None
            Output: Daily learning generation scheduled for configured time
        """
        try:
            logger.info("Setting up scheduled tasks...")

            # Schedule daily learning generation
            self.scheduler.add_daily_job(
                job_id="daily_learning",
                func=self._execute_daily_learning,
                time=settings.daily_learning_time,
            )
            logger.info(f"✓ Daily learning scheduled for {settings.daily_learning_time}")

        except Exception as e:
            logger.error(f"Failed to setup tasks: {e}", exc_info=True)
            raise

    def _execute_daily_learning(self) -> None:
        """
        Execute daily learning generation task.

        Args:
            None

        Returns:
            None

        Errors:
            Exception: If execution fails.

        Example:
            Input: None
            Output: Daily learning content generated and stored
        """
        try:
            logger.info("=" * 80)
            logger.info("Executing daily learning generation...")
            logger.info("=" * 80)

            content = self.agent.daily_learning_task.generate_daily_content()

            logger.info("Daily Learning Generated:")
            logger.info(f"  - Proficiency: {content['proficiency']}")
            logger.info(f"  - Vocabulary items: {len(content['vocabulary'])}")
            logger.info(f"  - Generated at: {content['generated_at']}")
            logger.info("✓ Daily learning completed successfully")

        except Exception as e:
            logger.error(f"Daily learning generation failed: {e}", exc_info=True)

    def run(self) -> NoReturn:
        """
        Run the application with scheduler.

        This method starts the scheduler and keeps the application running,
        executing scheduled tasks at their designated times.

        Args:
            None

        Returns:
            NoReturn: Application runs indefinitely until interrupted.

        Errors:
            Exception: If execution fails.

        Example:
            Input: None
            Output: Application running with scheduled tasks executing daily
        """
        try:
            # Setup tasks
            self.setup_tasks()

            # Start scheduler
            self.scheduler.start()
            logger.info("✓ Scheduler started")

            # Display scheduled jobs
            jobs = self.scheduler.list_jobs()
            logger.info(f"\nScheduled Jobs ({len(jobs)} total):")
            for job in jobs:
                logger.info(f"  - {job['name']}: {job['trigger']}")

            logger.info("\nCommuCraft-AI is running. Press Ctrl+C to stop.")
            logger.info("=" * 80)

            # Keep application running
            while True:
                time.sleep(1)

        except Exception as e:
            logger.error(f"Application error: {e}", exc_info=True)
            self.shutdown()
            raise

    def interactive_mode(self) -> None:
        """
        Run the application in interactive mode for testing.

        Args:
            None

        Returns:
            None

        Errors:
            Exception: If execution fails.

        Example:
            Input: None
            Output: Interactive prompt for user to send messages to agent
        """
        try:
            logger.info("CommuCraft-AI Interactive Mode")
            logger.info("Type 'help' for available commands, 'quit' to exit")
            logger.info("=" * 80)

            while True:
                try:
                    user_input = input("\nYou: ").strip()

                    if not user_input:
                        continue

                    if user_input.lower() == "quit":
                        logger.info("Exiting interactive mode...")
                        break

                    if user_input.lower() == "help":
                        self._show_help()
                        continue

                    if user_input.lower() == "status":
                        jobs = self.scheduler.list_jobs()
                        logger.info(f"Scheduler Status: {'Running' if self.scheduler.is_running() else 'Stopped'}")
                        logger.info(f"Scheduled Jobs: {len(jobs)}")
                        continue

                    # Process user input with agent
                    logger.info("Agent is processing...")
                    response = self.agent.run(user_input)
                    logger.info(f"Agent: {response}")

                except KeyboardInterrupt:
                    logger.info("Interrupted by user")
                    break
                except Exception as e:
                    logger.error(f"Error processing input: {e}")

        except Exception as e:
            logger.error(f"Interactive mode error: {e}", exc_info=True)

    def _show_help(self) -> None:
        """
        Display help information.

        Args:
            None

        Returns:
            None

        Errors:
            None
        """
        help_text = """
CommuCraft-AI - Professional Communication Coach

Available Commands:
  help              - Show this help message
  status            - Show scheduler status
  quit              - Exit interactive mode

Available Agent Functions:
  - Daily Learning: Request daily vocabulary and communication insights
  - Message Rewriting: Ask to rewrite emails, messages, or documents
  - Meeting Preparation: Get help preparing for meetings or calls

Example Requests:
  "Generate today's daily learning"
  "Help me rewrite this email: [your message]"
  "Prepare me for a meeting with my manager about the Q1 project"
        """
        logger.info(help_text)

    def shutdown(self) -> None:
        """
        Shutdown the application gracefully.

        Args:
            None

        Returns:
            None

        Errors:
            None
        """
        try:
            logger.info("=" * 80)
            logger.info("Shutting down CommuCraft-AI Application")
            logger.info("=" * 80)

            if self.scheduler.is_running():
                self.scheduler.stop()
                logger.info("✓ Scheduler stopped")

            self.agent.shutdown()
            logger.info("✓ Agent shutdown")

            logger.info("CommuCraft-AI shutdown complete")

        except Exception as e:
            logger.error(f"Error during shutdown: {e}", exc_info=True)


def main() -> None:
    """
    Main entry point for CommuCraft-AI application.

    Args:
        None

    Returns:
        None

    Errors:
        Exception: If execution fails.
    """
    try:
        app = CommuCraftApplication()

        # Check for command-line arguments
        if len(sys.argv) > 1:
            if sys.argv[1] == "--interactive" or sys.argv[1] == "-i":
                logger.info("Starting in interactive mode...")
                app.interactive_mode()
                return

        # Run in daemon mode with scheduler
        logger.info("Starting in daemon mode...")
        app.run()

    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
