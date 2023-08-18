"""Module for export folder command"""
import asyncio
import json
from mimetypes import guess_extension
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

    force_ext = None
    if kwargs["ext"] is not None:
        force_ext = "." + kwargs["ext"].split(".")[-1]

    with_meta = kwargs["with_metadata"]
    async for record in read_records_with_progress(
        entry, bucket, progress, sem, **kwargs
    ):
        if force_ext is None:
            # guess extension from content type
            guess = guess_extension(record.content_type)
            ext = guess if guess is not None else ".bin"
        else:
            ext = force_ext
        with open(entry_path / f"{record.timestamp}{ext}", "wb") as file:
            async for chunk in record.read(1024 * 512):
                file.write(chunk)
        if with_meta:
            with open(
                entry_path / f"{record.timestamp}.json", "w", encoding="utf-8"
            ) as file:
                json.dump(
                    {
                        "timestamp": record.timestamp,
                        "content_type": record.content_type,
                        "size": record.size,
                        "labels": record.labels,
                    },
                    file,
                    indent=4,
                )


async def export_to_folder(
    client: ReductClient,
    dest: str,
    bucket_name: str,
    **kwargs,
) -> None:
    """Export data from SRC bucket to DST folder"""
    async with client as client:
        bucket: Bucket = await client.get_bucket(bucket_name)
        folder_path = Path(dest)
        folder_path.mkdir(parents=True, exist_ok=True)
        sem = asyncio.Semaphore(kwargs["parallel"])

        with Progress() as progress:
            tasks = [
                _export_entry(folder_path, entry, bucket, progress, sem, **kwargs)
                for entry in filter_entries(
                    await bucket.get_entry_list(), kwargs["entries"]
                )
            ]
            await asyncio.gather(*tasks)
