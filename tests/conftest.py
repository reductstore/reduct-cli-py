"""Common fixtures"""
import time
from functools import partial
from pathlib import Path
from tempfile import gettempdir
from typing import Callable, Optional, List, Any

import pytest
from click.testing import CliRunner, Result
from reduct import Bucket, EntryInfo, Record, BucketSettings

from reduct_cli.cli import cli


class AsyncIter:  # pylint: disable=too-few-public-methods
    """Helper class for efficient mocking"""

    def __init__(self, items: Optional[List[Any]] = None):
        self.items = items if items else []

    async def __aiter__(self):
        for item in self.items:
            yield item


@pytest.fixture(name="runner")
def _make_runner() -> Callable[[str], Result]:
    runner = CliRunner()
    return partial(runner.invoke, cli, obj={})


@pytest.fixture(name="conf")
def _make_conf() -> Path:
    return Path(gettempdir()) / str(time.time_ns() % 1000000) / "config.toml"


@pytest.fixture(name="url")
def _make_url() -> str:
    return "http://127.0.0.1:8383"


@pytest.fixture(name="set_alias")
def _set_alias(runner, conf, url):
    runner(f"-c {conf} alias add test", input=f"{url}\ntoken\n")


@pytest.fixture(name="src_settings")
def _make_settings() -> BucketSettings:
    return BucketSettings()


@pytest.fixture(name="records")
def _make_records() -> List[Record]:
    def make_record(timestamp: int, data: bytes) -> Record:
        async def read_all():
            return data

        async def read(_n: int):
            yield data

        return Record(
            timestamp=timestamp, size=len(data), last=True, read_all=read_all, read=read
        )

    return [make_record(1000000000, b"Hey"), make_record(5000000000, b"Bye")]


@pytest.fixture(name="src_bucket")
def _make_src_bucket(mocker, src_settings, records) -> Bucket:
    bucket = mocker.Mock(spec=Bucket)
    bucket.name = "src_bucket"
    bucket.get_settings.return_value = src_settings
    bucket.get_entry_list.return_value = [
        EntryInfo(
            name="entry-1",
            size=1050000,
            block_count=1,
            record_count=2,
            oldest_record=1000000000,
            latest_record=5000000000,
        )
    ]

    bucket.query.return_value = AsyncIter(records)
    return bucket


@pytest.fixture(name="dest_bucket")
def _make_dest_bucket(mocker) -> Bucket:
    bucket = mocker.Mock(spec=Bucket)
    bucket.name = "dest_bucket"

    return bucket
