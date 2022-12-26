"""Helper functions"""
import time
from datetime import datetime
from pathlib import Path
from typing import Tuple

from click import Abort
from reduct import ReductError, EntryInfo, Bucket
from rich.progress import Progress

from reduct_cli.config import read_config, Alias
from reduct_cli.utils.consoles import error_console
from reduct_cli.utils.humanize import pretty_size


def get_alias(config_path: Path, name: str) -> Alias:
    """Helper method to parse alias from config"""
    conf = read_config(config_path)

    if name not in conf["aliases"]:
        error_console.print(f"Alias '{name}' doesn't exist")
        raise Abort()
    alias_: Alias = conf["aliases"][name]
    return alias_


def parse_path(path) -> Tuple[str, str]:
    """Parse path ALIAS/RESOURCE"""
    args = path.split("/")
    if len(args) != 2:
        raise RuntimeError(
            f"Path {path} has wrong format. It must be 'ALIAS/BUCKET_NAME'"
        )
    return tuple(args)


async def read_records_with_progress(
    entry: EntryInfo,
    bucket: Bucket,
    progress: Progress,
    **kwargs,
):
    """Read records from entry and show progress
    Args:
        entry (EntryInfo): Entry to read records from
        bucket (Bucket): Bucket to read records from
        progress (Progress): Progress bar to show progress
    Keyword Args:
        start (Optional[datetime]): Start time point
        stop (Optional[datetime]): Stop time point
    Yields:
        Record: Record from entry
    """

    def _to_timestamp(date: str) -> int:
        return int(datetime.fromisoformat(date).timestamp() * 1000_000)

    start = _to_timestamp(kwargs["start"]) if kwargs["start"] else entry.oldest_record
    stop = _to_timestamp(kwargs["stop"]) if kwargs["stop"] else entry.latest_record

    last_time = start
    task = progress.add_task(f"Entry '{entry.name}'", total=stop - start)
    exported_size = 0
    start_op = time.time()
    async for record in bucket.query(entry.name, start=start, stop=stop):
        try:
            exported_size += record.size
            yield record

        except ReductError as err:
            if err.status_code != 409:
                raise err

        progress.update(
            task,
            description=f"Entry '{entry.name}' (copied {pretty_size(exported_size)}, "
            f"speed {pretty_size(exported_size / (time.time() - start_op))}/s)",
            advance=record.timestamp - last_time,
            refresh=True,
        )
        last_time = record.timestamp

    progress.update(task, total=1, completed=True)
