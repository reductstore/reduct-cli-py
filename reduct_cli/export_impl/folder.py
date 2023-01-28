"""Module for export folder command"""
import asyncio
from pathlib import Path

from reduct import Client as ReductClient
from reduct import EntryInfo, Bucket
from rich.progress import Progress

from reduct_cli.utils.helpers import filter_entries, read_records_with_progress


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


async def export_to_folder(
    client: ReductClient,
    dest: str,
    bucket_name: str,
    parallel: int,
    **kwargs,
) -> None:
    """Export data from SRC bucket to DST folder"""
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