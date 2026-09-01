# time_utils.py
"""
Time and date utilities for the AI Teacher backend.

This module provides small, dependency-free helpers for:
- UTC timestamps
- Date/time formatting
- Duration calculations
- Human-readable durations
"""

from __future__ import annotations

from datetime import (
    date,
    datetime,
    timedelta,
    timezone,
)
from typing import Optional


UTC = timezone.utc


def utc_now() -> datetime:
    """
    Return the current UTC datetime.
    """

    return datetime.now(UTC)


def utc_today() -> date:
    """
    Return today's date in UTC.
    """

    return utc_now().date()


def ensure_utc(
    value: datetime,
) -> datetime:
    """
    Ensure a datetime is timezone-aware and represented in UTC.

    Naive datetimes are assumed to already represent UTC.
    """

    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)

    return value.astimezone(UTC)


def to_iso(
    value: Optional[datetime],
) -> Optional[str]:
    """
    Convert a datetime to an ISO-8601 string.
    """

    if value is None:
        return None

    return ensure_utc(value).isoformat()


def from_iso(
    value: str,
) -> datetime:
    """
    Parse an ISO-8601 datetime string.

    Naive values are treated as UTC.
    """

    if not value:
        raise ValueError(
            "Datetime string cannot be empty."
        )

    parsed = datetime.fromisoformat(
        value.replace("Z", "+00:00")
    )

    return ensure_utc(parsed)


def format_datetime(
    value: Optional[datetime],
    fmt: str = "%Y-%m-%d %H:%M:%S",
) -> Optional[str]:
    """
    Format a datetime using the supplied format.
    """

    if value is None:
        return None

    return ensure_utc(value).strftime(fmt)


def format_date(
    value: Optional[date],
    fmt: str = "%Y-%m-%d",
) -> Optional[str]:
    """
    Format a date.
    """

    if value is None:
        return None

    return value.strftime(fmt)


def add_minutes(
    value: datetime,
    minutes: int,
) -> datetime:
    """
    Add minutes to a datetime.
    """

    return value + timedelta(minutes=minutes)


def add_hours(
    value: datetime,
    hours: int,
) -> datetime:
    """
    Add hours to a datetime.
    """

    return value + timedelta(hours=hours)


def add_days(
    value: datetime,
    days: int,
) -> datetime:
    """
    Add days to a datetime.
    """

    return value + timedelta(days=days)


def minutes_between(
    start: datetime,
    end: datetime,
) -> float:
    """
    Return the number of minutes between two datetimes.
    """

    return (end - start).total_seconds() / 60


def seconds_between(
    start: datetime,
    end: datetime,
) -> float:
    """
    Return the number of seconds between two datetimes.
    """

    return (end - start).total_seconds()


def duration_to_seconds(
    duration: timedelta,
) -> float:
    """
    Convert a timedelta into seconds.
    """

    return duration.total_seconds()


def seconds_to_duration(
    seconds: float,
) -> timedelta:
    """
    Convert seconds into a timedelta.
    """

    return timedelta(seconds=seconds)


def humanize_duration(
    seconds: float,
) -> str:
    """
    Convert seconds into a human-readable duration.

    Examples:
        45 -> "45 seconds"
        90 -> "1 minute 30 seconds"
        3600 -> "1 hour"
    """

    total_seconds = max(0, int(seconds))

    days, remainder = divmod(
        total_seconds,
        86400,
    )

    hours, remainder = divmod(
        remainder,
        3600,
    )

    minutes, seconds = divmod(
        remainder,
        60,
    )

    parts: list[str] = []

    if days:
        parts.append(
            f"{days} day"
            f"{'s' if days != 1 else ''}"
        )

    if hours:
        parts.append(
            f"{hours} hour"
            f"{'s' if hours != 1 else ''}"
        )

    if minutes:
        parts.append(
            f"{minutes} minute"
            f"{'s' if minutes != 1 else ''}"
        )

    if seconds or not parts:
        parts.append(
            f"{seconds} second"
            f"{'s' if seconds != 1 else ''}"
        )

    return " ".join(parts)


def is_expired(
    value: datetime,
) -> bool:
    """
    Check whether a datetime has already passed.
    """

    return ensure_utc(value) <= utc_now()


def is_future(
    value: datetime,
) -> bool:
    """
    Check whether a datetime is in the future.
    """

    return ensure_utc(value) > utc_now()


def days_since(
    value: datetime,
) -> int:
    """
    Return the number of complete days since a datetime.
    """

    delta = utc_now() - ensure_utc(value)

    return max(
        0,
        delta.days,
    )


def get_week_start(
    value: Optional[date] = None,
) -> date:
    """
    Return the Monday of the week containing the given date.
    """

    current_date = value or utc_today()

    return current_date - timedelta(
        days=current_date.weekday()
    )


def get_week_end(
    value: Optional[date] = None,
) -> date:
    """
    Return the Sunday of the week containing the given date.
    """

    return get_week_start(value) + timedelta(days=6)


def is_same_day(
    first: datetime,
    second: datetime,
) -> bool:
    """
    Check whether two datetimes represent the same UTC date.
    """

    return (
        ensure_utc(first).date()
        == ensure_utc(second).date()
    )