"""
Scheduler for daily task execution using APScheduler.

This module manages scheduling of daily communication improvement tasks
to run at specified times each day.

Args:
    None

Returns:
    None

Errors:
    Exception: If scheduler initialization fails.
"""

import logging
from typing import Callable, Optional

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from sc_bot.config import settings

logger = logging.getLogger(__name__)


class TaskScheduler:
    """
    Manage scheduled execution of CommuCraft tasks using APScheduler.

    This class handles setting up and managing background job scheduling
    for daily learning generation and other periodic tasks.

    Args:
        None

    Returns:
        None

    Errors:
        Exception: If initialization fails.
    """

    def __init__(self) -> None:
        """
        Initialize task scheduler.

        Args:
            None

        Returns:
            None

        Errors:
            Exception: If scheduler initialization fails.
        """
        try:
            self.scheduler = BackgroundScheduler()
            self.jobs = {}
            logger.info("TaskScheduler initialized")
        except Exception as e:
            logger.error(f"Failed to initialize TaskScheduler: {e}")
            raise

    def add_daily_job(
        self,
        job_id: str,
        func: Callable,
        time: Optional[str] = None,
        args: tuple = (),
        kwargs: Optional[dict] = None,
    ) -> None:
        """
        Add a daily job to the scheduler.

        Args:
            job_id (str): Unique job identifier.
            func (Callable): Function to execute.
            time (Optional[str]): Time in HH:MM format (24-hour). Defaults to settings value.
            args (tuple): Positional arguments for the function. Defaults to empty tuple.
            kwargs (Optional[dict]): Keyword arguments for the function. Defaults to None.

        Returns:
            None

        Errors:
            ValueError: If time format is invalid.
            Exception: If job adding fails.

        Example:
            Input: job_id="daily_learning", func=generate_learning, time="09:00"
            Output: None (job scheduled)
        """
        if kwargs is None:
            kwargs = {}

        time_str = time or settings.daily_learning_time

        try:
            hour, minute = map(int, time_str.split(":"))

            # Create cron trigger for daily execution at specified time
            trigger = CronTrigger(hour=hour, minute=minute)

            job = self.scheduler.add_job(
                func=func,
                trigger=trigger,
                id=job_id,
                args=args,
                kwargs=kwargs,
                name=job_id,
                replace_existing=True,
            )

            self.jobs[job_id] = job
            logger.info(f"Job '{job_id}' scheduled for {time_str} daily")

        except ValueError as e:
            logger.error(f"Invalid time format '{time_str}': {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to add job '{job_id}': {e}")
            raise

    def add_cron_job(
        self,
        job_id: str,
        func: Callable,
        cron_schedule: str,
        args: tuple = (),
        kwargs: Optional[dict] = None,
    ) -> None:
        """
        Add a job with custom cron schedule.

        Args:
            job_id (str): Unique job identifier.
            func (Callable): Function to execute.
            cron_schedule (str): Cron expression (e.g., "0 9 * * MON" for 9 AM every Monday).
            args (tuple): Positional arguments. Defaults to empty tuple.
            kwargs (Optional[dict]): Keyword arguments. Defaults to None.

        Returns:
            None

        Errors:
            ValueError: If cron expression is invalid.
            Exception: If job adding fails.

        Example:
            Input: job_id="weekly_report", cron_schedule="0 18 * * FRI"
            Output: None (job scheduled for 6 PM every Friday)
        """
        if kwargs is None:
            kwargs = {}

        try:
            trigger = CronTrigger.from_crontab(cron_schedule)

            job = self.scheduler.add_job(
                func=func,
                trigger=trigger,
                id=job_id,
                args=args,
                kwargs=kwargs,
                name=job_id,
                replace_existing=True,
            )

            self.jobs[job_id] = job
            logger.info(f"Job '{job_id}' scheduled with cron '{cron_schedule}'")

        except ValueError as e:
            logger.error(f"Invalid cron expression '{cron_schedule}': {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to add cron job '{job_id}': {e}")
            raise

    def start(self) -> None:
        """
        Start the scheduler.

        Args:
            None

        Returns:
            None

        Errors:
            Exception: If scheduler fails to start.

        Example:
            Input: None
            Output: Scheduler running with all registered jobs
        """
        try:
            if not self.scheduler.running:
                self.scheduler.start()
                logger.info(f"Scheduler started with {len(self.jobs)} jobs")
        except Exception as e:
            logger.error(f"Failed to start scheduler: {e}")
            raise

    def stop(self) -> None:
        """
        Stop the scheduler.

        Args:
            None

        Returns:
            None

        Errors:
            Exception: If scheduler fails to stop.

        Example:
            Input: None
            Output: Scheduler stopped
        """
        try:
            if self.scheduler.running:
                self.scheduler.shutdown()
                logger.info("Scheduler stopped")
        except Exception as e:
            logger.error(f"Failed to stop scheduler: {e}")
            raise

    def remove_job(self, job_id: str) -> None:
        """
        Remove a scheduled job.

        Args:
            job_id (str): Job identifier to remove.

        Returns:
            None

        Errors:
            Exception: If job removal fails.

        Example:
            Input: "daily_learning"
            Output: None (job removed)
        """
        try:
            if job_id in self.jobs:
                self.scheduler.remove_job(job_id)
                del self.jobs[job_id]
                logger.info(f"Job '{job_id}' removed from scheduler")
        except Exception as e:
            logger.error(f"Failed to remove job '{job_id}': {e}")
            raise

    def get_job(self, job_id: str) -> Optional[dict]:
        """
        Get job information.

        Args:
            job_id (str): Job identifier.

        Returns:
            Optional[dict]: Job information or None if not found.

        Errors:
            None

        Example:
            Input: "daily_learning"
            Output: {"id": "daily_learning", "trigger": "..."}
        """
        if job_id not in self.jobs:
            return None

        job = self.jobs[job_id]
        return {
            "id": job.id,
            "name": job.name,
            "trigger": str(job.trigger),
        }

    def list_jobs(self) -> list[dict]:
        """
        List all scheduled jobs.

        Args:
            None

        Returns:
            list[dict]: List of job information.

        Errors:
            None

        Example:
            Input: None
            Output: [{"id": "daily_learning", "trigger": "..."}, ...]
        """
        jobs_info = []
        for job_id, job in self.jobs.items():
            jobs_info.append(
                {
                    "id": job.id,
                    "name": job.name,
                    "trigger": str(job.trigger),
                }
            )
        return jobs_info

    def is_running(self) -> bool:
        """
        Check if scheduler is running.

        Args:
            None

        Returns:
            bool: True if scheduler is running.

        Errors:
            None

        Example:
            Input: None
            Output: True
        """
        return self.scheduler.running
