"""Export Command"""
import asyncio
from asyncio import new_event_loop as loop
from pathlib import Path
from typing import Optional

import click
from reduct import Client as ReductClient, Bucket, EntryInfo
from rich.progress import Progress

from reduct_cli.utils.error import error_handle
from reduct_cli.utils.helpers import (
    parse_path,
    get_alias,
    read_records_with_progress,
    filter_entries,
)

run = loop().run_until_complete


@click.group()
def export():
    """Export data from a bucket somewhere else"""


async def _export_entry(
    path: Path, entry: EntryInfo, bucket: Bucket, progress: Progress, sem, **kwargs
) -> None:
    entry_path = Path(path / entry.name)
    entry_path.mkdir(exist_ok=True)

    async for record in read_records_with_progress(
        entry, bucket, progress, sem, **kwargs
    ):
        with open(entry_path / f"{record.timestamp}.bin", "wb") as file:
            async for chunk in record.read(1024):
                file.write(chunk)


async def _export_bucket(
    client: ReductClient,
    dest: str,
    bucket_name: str,
    parallel: int,
    **kwargs,
) -> None:
    bucket: Bucket = await client.get_bucket(bucket_name)
    folder_path = Path(dest) / bucket_name
    folder_path.mkdir(parents=True, exist_ok=True)
    sem = asyncio.Semaphore(parallel)

    with Progress() as progress:
        tasks = [
            _export_entry(folder_path, entry, bucket, progress, sem, **kwargs)
            for entry in filter_entries(
                await bucket.get_entry_list(), kwargs["entries"]
            )
        ]
        await asyncio.gather(*tasks)


@export.command()
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
@click.option(
    "--entries",
    help="Mirror only these entries, separated by comma",
    default="",
)
@click.pass_context
def folder(
    ctx, src: str, dest: str, start: Optional[str], stop: Optional[str], entries: str
):  # pylint: disable=too-many-arguments
    """Export data from SRC bucket to DST folder

    SRC should be in the format of ALIAS/BUCKET_NAME
    """

    with error_handle():
        alias_name, bucket = parse_path(src)
        alias = get_alias(ctx.obj["config_path"], alias_name)

        client = ReductClient(
            alias["url"], api_token=alias["token"], timeout=ctx.obj["timeout"]
        )
        run(
            _export_bucket(
                client,
                dest,
                bucket,
                parallel=ctx.obj["parallel"],
                start=start,
                stop=stop,
                entries=entries.split(","),
            )
        )
