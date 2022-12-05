"""Mirror command"""
import asyncio
import time
from datetime import datetime
from typing import Optional

import click
from rich.progress import Progress
from reduct import Client as ReductClient, ReductError, Bucket, EntryInfo

from reduct_cli.utils.error import error_handle
from reduct_cli.utils.helpers import parse_path, get_alias
from reduct_cli.utils.humanize import pretty_size


async def _sync_entry(
    entry: EntryInfo,
    src_bucket: Bucket,
    dest_bucket: Bucket,
    progress: Progress,
    **kwargs,
):
    progress_start = kwargs["start"] if kwargs["start"] else entry.oldest_record
    progress_stop = kwargs["stop"] if kwargs["stop"] else entry.latest_record
    last_time = progress_start
    task = progress.add_task(
        f"Entry '{entry.name}'", total=progress_stop - progress_start
    )
    mirrored_size = 0
    start_op = time.time()
    async for record in src_bucket.query(
        entry.name, start=kwargs["start"], stop=kwargs["stop"]
    ):
        try:
            mirrored_size += record.size
            await dest_bucket.write(
                entry.name,
                data=record.read(1024),
                content_length=record.size,
                timestamp=record.timestamp,
            )
        except ReductError as err:
            if err.status_code != 409:
                raise err

        progress.update(
            task,
            description=f"Entry '{entry.name}' (copied {pretty_size(mirrored_size)}, "
            f"speed {pretty_size(mirrored_size / (time.time() - start_op))}/s)",
            advance=record.timestamp - last_time,
            refresh=True,
        )
        last_time = record.timestamp

    progress.update(task, total=1, completed=True)


async def _sync_bucket(
    src_bucket_name: str,
    dest_bucket_name: str,
    src: ReductClient,
    dest: ReductClient,
    **kwargs,
) -> None:
    src_bucket: Bucket = await src.get_bucket(src_bucket_name)
    dest_bucket: Bucket = await dest.create_bucket(
        dest_bucket_name, settings=await src_bucket.get_settings(), exist_ok=True
    )
    with Progress() as progress:
        tasks = [
            _sync_entry(entry, src_bucket, dest_bucket, progress, **kwargs)
            for entry in await src_bucket.get_entry_list()
        ]
        await asyncio.gather(*tasks)


@click.command()
@click.argument("src")
@click.argument("dest")
@click.option(
    "--start",
    help="Mirror records with timestamps newer than this time point in ISO format",
)
@click.option(
    "--stop",
    help="Mirror records  with timestamps older than this time point in ISO format",
)
@click.pass_context
def mirror(ctx, src: str, dest: str, start: Optional[str], stop: Optional[str]):
    """Copy data from a bucket to another one

    If the destination bucket doesn't exist, it is created with the settings of the"""

    with error_handle():
        alias_name, src_bucket = parse_path(src)
        alias = get_alias(ctx.obj["config_path"], alias_name)
        src_instance = ReductClient(
            alias["url"], api_token=alias["token"], timeout=ctx.obj["timeout"]
        )

        alias_name, dest_bucket = parse_path(dest)
        alias = get_alias(ctx.obj["config_path"], alias_name)
        dest_instance = ReductClient(
            alias["url"], api_token=alias["token"], timeout=ctx.obj["timeout"]
        )

        if start:
            start = int(datetime.fromisoformat(start).timestamp() * 1000_000)

        if stop:
            stop = int(datetime.fromisoformat(stop).timestamp() * 1000_000)

        asyncio.new_event_loop().run_until_complete(
            _sync_bucket(
                src_bucket,
                dest_bucket,
                src_instance,
                dest_instance,
                start=start,
                stop=stop,
            )
        )
