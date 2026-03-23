"""
Unit tests for CommuCraft-AI scheduler module.

Tests the APScheduler integration for task scheduling.

Args:
    None

Returns:
    None

Errors:
    pytest fixtures and assertions
"""

import pytest

from src.sc_bot.scheduler import TaskScheduler


@pytest.fixture
def scheduler() -> TaskScheduler:
    """
    Create scheduler instance for testing.

    Args:
        None

    Returns:
        TaskScheduler: Scheduler instance.

    Errors:
        None
    """
    return TaskScheduler()


def test_scheduler_initialization(scheduler: TaskScheduler) -> None:
    """
    Test scheduler initialization.

    Args:
        scheduler (TaskScheduler): Scheduler instance.

    Returns:
        None

    Errors:
        AssertionError: If test fails.
    """
    assert scheduler is not None
    assert not scheduler.is_running()


def test_add_daily_job(scheduler: TaskScheduler) -> None:
    """
    Test adding a daily job.

    Args:
        scheduler (TaskScheduler): Scheduler instance.

    Returns:
        None

    Errors:
        AssertionError: If test fails.
    """

    def test_func() -> str:
        return "Test"

    scheduler.add_daily_job("test_job", test_func, time="09:00")
    assert "test_job" in scheduler.jobs


def test_add_daily_job_invalid_time(scheduler: TaskScheduler) -> None:
    """
    Test adding daily job with invalid time format.

    Args:
        scheduler (TaskScheduler): Scheduler instance.

    Returns:
        None

    Errors:
        AssertionError: If test fails.
    """

    def test_func() -> str:
        return "Test"

    with pytest.raises(ValueError):
        scheduler.add_daily_job("test_job", test_func, time="25:00")


def test_add_cron_job(scheduler: TaskScheduler) -> None:
    """
    Test adding a cron job.

    Args:
        scheduler (TaskScheduler): Scheduler instance.

    Returns:
        None

    Errors:
        AssertionError: If test fails.
    """

    def test_func() -> str:
        return "Test"

    scheduler.add_cron_job("test_cron", test_func, "0 9 * * *")
    assert "test_cron" in scheduler.jobs


def test_start_stop_scheduler(scheduler: TaskScheduler) -> None:
    """
    Test starting and stopping scheduler.

    Args:
        scheduler (TaskScheduler): Scheduler instance.

    Returns:
        None

    Errors:
        AssertionError: If test fails.
    """

    def test_func() -> str:
        return "Test"

    scheduler.add_daily_job("test_job", test_func, time="09:00")
    scheduler.start()

    assert scheduler.is_running()

    scheduler.stop()
    assert not scheduler.is_running()


def test_get_job(scheduler: TaskScheduler) -> None:
    """
    Test getting job information.

    Args:
        scheduler (TaskScheduler): Scheduler instance.

    Returns:
        None

    Errors:
        AssertionError: If test fails.
    """

    def test_func() -> str:
        return "Test"

    scheduler.add_daily_job("test_job", test_func, time="09:00")
    job_info = scheduler.get_job("test_job")

    assert job_info is not None
    assert job_info["id"] == "test_job"


def test_get_nonexistent_job(scheduler: TaskScheduler) -> None:
    """
    Test getting non-existent job.

    Args:
        scheduler (TaskScheduler): Scheduler instance.

    Returns:
        None

    Errors:
        AssertionError: If test fails.
    """
    job_info = scheduler.get_job("nonexistent")
    assert job_info is None


def test_list_jobs(scheduler: TaskScheduler) -> None:
    """
    Test listing all jobs.

    Args:
        scheduler (TaskScheduler): Scheduler instance.

    Returns:
        None

    Errors:
        AssertionError: If test fails.
    """

    def test_func1() -> str:
        return "Test1"

    def test_func2() -> str:
        return "Test2"

    scheduler.add_daily_job("job1", test_func1, time="09:00")
    scheduler.add_daily_job("job2", test_func2, time="10:00")

    jobs = scheduler.list_jobs()
    assert len(jobs) == 2


def test_remove_job(scheduler: TaskScheduler) -> None:
    """
    Test removing a job.

    Args:
        scheduler (TaskScheduler): Scheduler instance.

    Returns:
        None

    Errors:
        AssertionError: If test fails.
    """

    def test_func() -> str:
        return "Test"

    scheduler.add_daily_job("test_job", test_func, time="09:00")
    assert "test_job" in scheduler.jobs

    scheduler.remove_job("test_job")
    assert "test_job" not in scheduler.jobs


def test_job_with_args(scheduler: TaskScheduler) -> None:
    """
    Test job with arguments.

    Args:
        scheduler (TaskScheduler): Scheduler instance.

    Returns:
        None

    Errors:
        AssertionError: If test fails.
    """

    def test_func(arg1: str, arg2: str) -> str:
        return f"{arg1} {arg2}"

    scheduler.add_daily_job("test_job", test_func, time="09:00", args=("Hello", "World"))
    assert "test_job" in scheduler.jobs


def test_job_with_kwargs(scheduler: TaskScheduler) -> None:
    """
    Test job with keyword arguments.

    Args:
        scheduler (TaskScheduler): Scheduler instance.

    Returns:
        None

    Errors:
        AssertionError: If test fails.
    """

    def test_func(message: str = "default") -> str:
        return message

    scheduler.add_daily_job("test_job", test_func, time="09:00", kwargs={"message": "Custom"})
    assert "test_job" in scheduler.jobs
