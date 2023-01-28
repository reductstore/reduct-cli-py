"""Module for export store command"""
import asyncio

from reduct import Client as ReductClient, Bucket, EntryInfo, ReductError
from rich.progress import Progress

from reduct_cli.utils.helpers import (
    read_records_with_progress,
    filter_entries,
)


async def _copy_entry(
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
                data=record.read(1024 * 512),
                content_length=record.size,
                timestamp=record.timestamp,
                content_type=record.content_type,
                labels=record.labels,
            )
        except ReductError as err:
            # filter out the error that the entry already exists
            if err.status_code != 409:
                raise err


async def export_to_bucket(
    src_bucket_name: str,
    dest_bucket_name: str,
    src: ReductClient,
    dest: ReductClient,
    parallel: int,
    **kwargs,
) -> None:
    """Export data from SRC bucket to DST bucket"""
    src_bucket: Bucket = await src.get_bucket(src_bucket_name)
    dest_bucket: Bucket = await dest.create_bucket(
        dest_bucket_name, settings=await src_bucket.get_settings(), exist_ok=True
    )

    sem = asyncio.Semaphore(parallel)
    with Progress() as progress:
        tasks = [
            _copy_entry(entry, src_bucket, dest_bucket, progress, sem, **kwargs)
            for entry in filter_entries(
                await src_bucket.get_entry_list(), kwargs["entries"]
            )
        ]
        await asyncio.gather(*tasks)
