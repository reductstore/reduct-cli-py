"""Unit tests for helpers"""
from asyncio import Semaphore

import pytest
from reduct import EntryInfo
from rich.progress import Progress

from reduct_cli.utils.helpers import read_records_with_progress


@pytest.fixture(name="progress")
def _make_progress(mocker):
    return mocker.Mock(spec=Progress)


@pytest.fixture(name="default_kwargs")
def _make_default_kwargs():
    return dict(
        sem=Semaphore(1),
        include={},
        exclude={},
        timeout=0,
        parallel=1,
    )


@pytest.fixture(name="entry")
def _make_entry(mocker):
    entry_info = mocker.Mock(spec=EntryInfo)
    entry_info.name = "entry-1"
    return entry_info


@pytest.mark.parametrize(
    "start,stop",
    [("1000000000", "5000000000"), ("2001-09-09T00:00:00", "2028-09-09T00:00:00")],
)
@pytest.mark.asyncio
async def test__read_records_with_progress_with_integers(
    entry, src_bucket, start, stop, progress, default_kwargs
):
    """Should read records with integers or ISO time strings"""

    result = [
        record
        async for record in read_records_with_progress(
            entry,
            src_bucket,
            progress,
            start=start,
            stop=stop,
            **default_kwargs,
        )
    ]

    assert len(result) == 2
    assert result[0].timestamp == 1000000000
    assert result[1].timestamp == 5000000000
