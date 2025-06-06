"""
Date and time utilities for FlashGenie.

This module provides utility functions for date/time operations,
formatting, and calculations used in spaced repetition.
"""

from datetime import datetime, timedelta, date
from typing import Optional, Union


def now() -> datetime:
    """Get current datetime."""
    return datetime.now()


def today() -> date:
    """Get current date."""
    return date.today()


def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format a datetime object as a string.
    
    Args:
        dt: Datetime to format
        format_str: Format string
        
    Returns:
        Formatted datetime string
    """
    return dt.strftime(format_str)


def format_date(d: date, format_str: str = "%Y-%m-%d") -> str:
    """
    Format a date object as a string.
    
    Args:
        d: Date to format
        format_str: Format string
        
    Returns:
        Formatted date string
    """
    return d.strftime(format_str)


def parse_datetime(date_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> datetime:
    """
    Parse a datetime string.
    
    Args:
        date_str: String to parse
        format_str: Expected format
        
    Returns:
        Parsed datetime
    """
    return datetime.strptime(date_str, format_str)


def parse_iso_datetime(date_str: str) -> datetime:
    """
    Parse an ISO format datetime string.
    
    Args:
        date_str: ISO datetime string
        
    Returns:
        Parsed datetime
    """
    return datetime.fromisoformat(date_str)


def days_between(start: Union[datetime, date], end: Union[datetime, date]) -> int:
    """
    Calculate the number of days between two dates.
    
    Args:
        start: Start date/datetime
        end: End date/datetime
        
    Returns:
        Number of days (can be negative)
    """
    if isinstance(start, datetime):
        start = start.date()
    if isinstance(end, datetime):
        end = end.date()
    
    return (end - start).days


def hours_between(start: datetime, end: datetime) -> float:
    """
    Calculate the number of hours between two datetimes.
    
    Args:
        start: Start datetime
        end: End datetime
        
    Returns:
        Number of hours (can be negative)
    """
    delta = end - start
    return delta.total_seconds() / 3600


def add_days(dt: Union[datetime, date], days: int) -> Union[datetime, date]:
    """
    Add days to a date or datetime.
    
    Args:
        dt: Date or datetime to modify
        days: Number of days to add
        
    Returns:
        Modified date or datetime
    """
    return dt + timedelta(days=days)


def add_hours(dt: datetime, hours: float) -> datetime:
    """
    Add hours to a datetime.
    
    Args:
        dt: Datetime to modify
        hours: Number of hours to add
        
    Returns:
        Modified datetime
    """
    return dt + timedelta(hours=hours)


def is_same_day(dt1: Union[datetime, date], dt2: Union[datetime, date]) -> bool:
    """
    Check if two dates/datetimes are on the same day.
    
    Args:
        dt1: First date/datetime
        dt2: Second date/datetime
        
    Returns:
        True if same day
    """
    if isinstance(dt1, datetime):
        dt1 = dt1.date()
    if isinstance(dt2, datetime):
        dt2 = dt2.date()
    
    return dt1 == dt2


def is_past(dt: Union[datetime, date]) -> bool:
    """
    Check if a date/datetime is in the past.
    
    Args:
        dt: Date or datetime to check
        
    Returns:
        True if in the past
    """
    if isinstance(dt, datetime):
        return dt < now()
    else:
        return dt < today()


def is_future(dt: Union[datetime, date]) -> bool:
    """
    Check if a date/datetime is in the future.
    
    Args:
        dt: Date or datetime to check
        
    Returns:
        True if in the future
    """
    if isinstance(dt, datetime):
        return dt > now()
    else:
        return dt > today()


def time_until(target: datetime) -> timedelta:
    """
    Calculate time until a target datetime.
    
    Args:
        target: Target datetime
        
    Returns:
        Time delta until target
    """
    return target - now()


def time_since(past: datetime) -> timedelta:
    """
    Calculate time since a past datetime.
    
    Args:
        past: Past datetime
        
    Returns:
        Time delta since past
    """
    return now() - past


def format_duration(delta: timedelta) -> str:
    """
    Format a timedelta as a human-readable string.
    
    Args:
        delta: Time delta to format
        
    Returns:
        Formatted duration string
    """
    total_seconds = int(delta.total_seconds())
    
    if total_seconds < 0:
        return "0 seconds"
    
    days = total_seconds // 86400
    hours = (total_seconds % 86400) // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    
    parts = []
    
    if days > 0:
        parts.append(f"{days} day{'s' if days != 1 else ''}")
    
    if hours > 0:
        parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
    
    if minutes > 0:
        parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
    
    if seconds > 0 or not parts:
        parts.append(f"{seconds} second{'s' if seconds != 1 else ''}")
    
    if len(parts) == 1:
        return parts[0]
    elif len(parts) == 2:
        return f"{parts[0]} and {parts[1]}"
    else:
        return f"{', '.join(parts[:-1])}, and {parts[-1]}"


def format_relative_time(dt: datetime) -> str:
    """
    Format a datetime as relative time (e.g., "2 hours ago", "in 3 days").
    
    Args:
        dt: Datetime to format
        
    Returns:
        Relative time string
    """
    delta = now() - dt
    
    if delta.total_seconds() < 0:
        # Future time
        future_delta = -delta
        duration_str = format_duration(future_delta)
        return f"in {duration_str}"
    else:
        # Past time
        duration_str = format_duration(delta)
        return f"{duration_str} ago"


def get_next_review_date(last_review: Optional[datetime], 
                        interval_days: int) -> datetime:
    """
    Calculate the next review date based on interval.
    
    Args:
        last_review: Last review datetime (None for new cards)
        interval_days: Interval in days
        
    Returns:
        Next review datetime
    """
    if last_review is None:
        base_date = now()
    else:
        base_date = last_review
    
    return base_date + timedelta(days=interval_days)


def get_study_streak_days(study_dates: list[date]) -> int:
    """
    Calculate consecutive study streak from a list of study dates.
    
    Args:
        study_dates: List of dates when studying occurred
        
    Returns:
        Number of consecutive days
    """
    if not study_dates:
        return 0
    
    # Sort dates in descending order
    sorted_dates = sorted(set(study_dates), reverse=True)
    
    # Count consecutive days from today
    current_date = today()
    streak = 0
    
    for study_date in sorted_dates:
        expected_date = current_date - timedelta(days=streak)
        
        if study_date == expected_date:
            streak += 1
        else:
            break
    
    return streak


def get_week_start(dt: Union[datetime, date]) -> date:
    """
    Get the start of the week (Monday) for a given date.
    
    Args:
        dt: Date or datetime
        
    Returns:
        Date of the Monday of that week
    """
    if isinstance(dt, datetime):
        dt = dt.date()
    
    days_since_monday = dt.weekday()
    return dt - timedelta(days=days_since_monday)


def get_month_start(dt: Union[datetime, date]) -> date:
    """
    Get the start of the month for a given date.
    
    Args:
        dt: Date or datetime
        
    Returns:
        Date of the first day of that month
    """
    if isinstance(dt, datetime):
        dt = dt.date()
    
    return dt.replace(day=1)
