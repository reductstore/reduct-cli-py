"""Helper function for readable time intervals and volumes"""

MINUTE = 60
HOUR = MINUTE * 60
DAY = HOUR * 24
WEEK = DAY * 7
MONTH = DAY * 30
YEAR = MONTH * 12


def time_interval(seconds: int) -> str:  # pylint:disable=too-many-return-statements
    """Print readable time interval"""
    if seconds < 0:
        raise ValueError("Seconds must be positive")

    if seconds <= MINUTE:
        return f"{seconds} second(s)"
    if seconds <= HOUR:
        return f"{int(seconds / MINUTE)} minute(s)"
    if seconds <= DAY:
        return f"{int(seconds / HOUR)} hour(s)"
    if seconds <= WEEK:
        return f"{int(seconds / DAY)} day(s)"
    if seconds <= MONTH:
        return f"{int(seconds / WEEK)} week(s)"
    if seconds <= YEAR:
        return f"{int(seconds / MONTH)} month(s)"

    return f"{int(seconds / YEAR)} year(s)"


KB = 1000
MB = KB * 1000
GB = MB * 1000
TB = GB * 1000


def data_size(size: int) -> str:
    """Return human-readable size"""
    if size < 0:
        raise ValueError("Size must be positive")

    if size <= KB:
        return f"{size} B"
    if size <= MB:
        return f"{int(size / KB)} KB"
    if size <= GB:
        return f"{int(size / MB)} MB"
    if size <= TB:
        return f"{int(size / GB)} GB"

    return f"{int(size / TB)} TB"
