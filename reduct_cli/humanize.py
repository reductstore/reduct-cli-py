"""Helper function for readable time intervals and volumes"""
# pylint:disable=too-many-return-statements
from datetime import datetime, timezone
from typing import Union

MINUTE = 60
HOUR = MINUTE * 60
DAY = HOUR * 24
WEEK = DAY * 7
MONTH = DAY * 30
YEAR = MONTH * 12


def pretty_time_interval(seconds: Union[int, float]) -> str:
    """Print readable time interval"""
    if seconds < 0:
        raise ValueError("Seconds must be positive")

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


def pretty_size(size: int) -> str:
    """Return human-readable size"""
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
