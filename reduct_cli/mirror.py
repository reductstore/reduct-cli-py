"""Mirror command"""
import asyncio
from typing import Optional

import click
from reduct import Client as ReductClient, Bucket, EntryInfo, ReductError
from rich.progress import Progress

from reduct_cli.utils.error import error_handle
from reduct_cli.utils.helpers import (
    parse_path,
    get_alias,
    read_records_with_progress,
    filter_entries,
)


async def _sync_entry(
    entry: EntryInfo,
    src_bucket: Bucket,
    dest_bucket: Bucket,
    progress: Progress,
    sem: asyncio.Semaphore,
    **kwargs,
):
    async for record in read_records_with_progress(
        entry, src_bucket, progress, sem, **kwargs
    ):
        try:
            await dest_bucket.write(
                entry.name,
                data=record.read(1024),
                content_length=record.size,
                timestamp=record.timestamp,
            )
        except ReductError as err:
            # filter out the error that the entry already exists
            if err.status_code != 409:
                raise err


async def _sync_bucket(
    src_bucket_name: str,
    dest_bucket_name: str,
    src: ReductClient,
    dest: ReductClient,
    parallel: int,
    **kwargs,
) -> None:
    src_bucket: Bucket = await src.get_bucket(src_bucket_name)
    dest_bucket: Bucket = await dest.create_bucket(
        dest_bucket_name, settings=await src_bucket.get_settings(), exist_ok=True
    )

    sem = asyncio.Semaphore(parallel)
    with Progress() as progress:
        tasks = [
            _sync_entry(entry, src_bucket, dest_bucket, progress, sem, **kwargs)
            for entry in filter_entries(
                await src_bucket.get_entry_list(), kwargs["entries"]
            )
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
@click.option(
    "--entries",
    help="Mirror only these entries, separated by comma",
    default="",
)
@click.pass_context
def mirror(
    ctx, src: str, dest: str, start: Optional[str], stop: Optional[str], entries: str
):  # pylint: disable=too-many-arguments
    """Copy data from SRC to DST bucket

    SRC and DST should be in the format of ALIAS/BUCKET_NAME

    If the destination bucket doesn't exist, it is created with
    the settings of the source bucket."""

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

        asyncio.new_event_loop().run_until_complete(
            _sync_bucket(
                src_bucket,
                dest_bucket,
                src_instance,
                dest_instance,
                parallel=ctx.obj["parallel"],
                start=start,
                stop=stop,
                entries=entries.split(","),
            )
        )
