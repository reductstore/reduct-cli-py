"""Helper function for readable time intervals and volumes"""
# pylint:disable=too-many-return-statements
from datetime import datetime, timezone
from typing import Union, Optional

MINUTE = 60
HOUR = MINUTE * 60
DAY = HOUR * 24
WEEK = DAY * 7
MONTH = DAY * 30
YEAR = MONTH * 12


def pretty_time_interval(seconds: Union[int, float]) -> str:
    """Print readable time interval"""
    if seconds < 0:
        return "---"

    if seconds <= MINUTE:
        return f"{round(seconds)} second(s)"
    if seconds <= HOUR:
        return f"{round(seconds / MINUTE)} minute(s)"
    if seconds <= DAY:
        return f"{round(seconds / HOUR)} hour(s)"
    if seconds <= WEEK:
        return f"{round(seconds / DAY)} day(s)"
    if seconds <= MONTH:
        return f"{round(seconds / WEEK)} week(s)"
    if seconds <= YEAR:
        return f"{round(seconds / MONTH)} month(s)"

    return f"{round(seconds / YEAR)} year(s)"


KB = 1000
MB = KB * 1000
GB = MB * 1000
TB = GB * 1000


def pretty_size(size: Union[int, float]) -> str:
    """Return human-readable size"""

    size = int(size)
    if size < 0:
        raise ValueError("Size must be positive")

    if size <= KB:
        return f"{size} B"
    if size <= MB:
        return f"{round(size / KB)} KB"
    if size <= GB:
        return f"{round(size / MB)} MB"
    if size <= TB:
        return f"{round(size / GB)} GB"

    return f"{round(size / TB)} TB"


def print_datetime(time_stamp: int, valid: bool):
    """Print datatime as ISO string in UTC or '---' if it's invalid"""
    return (
        datetime.fromtimestamp(time_stamp / 1000_000, tz=timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%S"
        )
        if valid
        else "---"
    )


def parse_ci_size(size: Optional[str]) -> Optional[int]:
    """Parse CI size and return size in bytes"""
    if size is None:
        return None

    size = size.strip().upper()
    if "TB" in size:
        return int(size.replace("TB", "")) * TB
    if "GB" in size:
        return int(size.replace("GB", "")) * GB
    if "MB" in size:
        return int(size.replace("MB", "")) * MB
    if "KB" in size:
        return int(size.replace("KB", "")) * KB
    if "B" in size:
        return int(size.replace("B", ""))

    raise ValueError(f"Failed to parse {size}")
