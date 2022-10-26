"""Unit tests for bucket commands"""
import re

import pytest
from reduct import BucketInfo, Client


@pytest.fixture(name="client")
def _make_client(mocker) -> Client:
    kls = mocker.patch("reduct_cli.bucket.ReductClient")
    kls.return_value = mocker.Mock(spec=Client)
    kls.return_value.list.return_value = [
        BucketInfo(
            name="bucket-1",
            entry_count=1,
            size=1050000,
            oldest_record=1000000000,
            latest_record=5000000000,
        ),
        BucketInfo(
            name="bucket-2",
            entry_count=5,
            size=50000,
            oldest_record=6000000000,
            latest_record=8000000000,
        ),
    ]
    return kls.return_value


@pytest.mark.usefixtures("set_alias")
def test__get_short_list(runner, conf, client):
    """Should print list of buckets"""

    result = runner(f"-c {conf} bucket ls test")
    assert result.exit_code == 0
    assert result.output.split("\n") == ["bucket-1", "bucket-2", ""]


@pytest.mark.usefixtures("set_alias")
def test__get_full_list(runner, conf, client):
    """Should print buckets as a table with full information"""

    def split_and_strip(src: str, sep: str):
        return [s.strip() for s in src.split(sep) if len(s) > 0]

    result = runner(f"-c {conf} bucket ls --full test")
    assert result.exit_code == 0
    header = result.output.split("\n")[1]
    assert split_and_strip(header, "┃") == [
        "Name",
        "Entry Count",
        "Size",
        "Oldest Record",
        "Latest Record",
    ]

    buckets = result.output.split("\n")[3:5]
    assert [split_and_strip(bucket, "│") for bucket in buckets] == [
        ["bucket-1", "1", "1 MB", "1970-01-01T01:1…", "1970-01-01T02:2…"],
        ["bucket-2", "5", "50 KB", "1970-01-01T02:4…", "1970-01-01T03:1…"],
    ]

    total = result.output.split("\n")[6]
    assert split_and_strip(total, "│") == [
        "Total for 2",
        "6",
        "1 MB",
        "1970-01-01T01:1…",
        "1970-01-01T03:1…",
    ]


@pytest.mark.usefixtures("set_alias")
def test__get_error(runner, conf, client):
    """Should print error if something got wrong"""
    client.list.side_effect = RuntimeError("Oops")
    result = runner(f"-c {conf} bucket ls test")
    assert result.exit_code == 0
    assert result.output == "Status: Error\nOops\n"
