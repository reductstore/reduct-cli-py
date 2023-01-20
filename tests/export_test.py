"""Unit tests for export command"""
from pathlib import Path
from tempfile import gettempdir
from unittest.mock import call, ANY

import pytest
from reduct import Client


@pytest.fixture(name="client")
def _make_client(mocker, src_bucket) -> Client:
    kls = mocker.patch("reduct_cli.export.ReductClient")
    client = mocker.Mock(spec=Client)
    client.get_bucket.return_value = src_bucket

    kls.return_value = client
    return client


@pytest.mark.usefixtures("set_alias", "client")
def test__export_to_folder_ok_with_interval(runner, conf, src_bucket, records):
    """Should export a bucket to a fodder one with time interval"""
    path = Path(gettempdir()) / "reduct-test"
    result = runner(
        f"-c {conf} export folder --start 2022-01-02T00:00:01.100300+02:00 "
        f"--stop 2022-02-01T00:00:00+02:00 "
        f"test/src_bucket {path}"
    )
    assert "Entry 'entry-1' (copied 1 records (6 B)" in result.output
    assert result.exit_code == 0

    assert src_bucket.query.call_args_list == [
        call("entry-1", start=1641074401100300, stop=1643666400000000),
        call("entry-2", start=1641074401100300, stop=1643666400000000),
    ]

    assert (
        path / "src_bucket" / "entry-1" / f"{records[0].timestamp}.bin"
    ).read_bytes() == b"Hey"
    assert (
        path / "src_bucket" / "entry-2" / f"{records[1].timestamp}.bin"
    ).read_bytes() == b"Bye"


@pytest.mark.usefixtures("set_alias", "client")
def test__export_to_folder_ok_without_interval(runner, conf, src_bucket, records):
    """Should export a bucket to a fodder one without time interval"""
    path = Path(gettempdir()) / "reduct-test"
    result = runner(f"-c {conf} export folder test/src_bucket {path}")
    assert "Entry 'entry-1' (copied 1 records (6 B)" in result.output
    assert result.exit_code == 0

    assert src_bucket.query.call_args_list[0] == call(
        "entry-1", start=1000000000, stop=5000000000
    )


@pytest.mark.usefixtures("set_alias")
def test__export_to_folder_fail(runner, client, conf):
    """Should fail if the destination folder does not exist"""
    client.get_bucket.side_effect = RuntimeError("Oops")

    result = runner(f"-c {conf} export folder test/src_bucket .")
    assert result.output == "[RuntimeError] Oops\nAborted!\n"
    assert result.exit_code == 1


@pytest.mark.usefixtures("set_alias", "client")
def test__export_utc_timestamp(runner, conf, src_bucket):
    """Should support Z designator for UTC timestamps"""
    result = runner(
        f"-c {conf} export folder test/src_bucket . "
        f"--start 2022-01-02T00:00:01.100300Z --stop 2022-02-01T00:00:00Z"
    )
    assert result.exit_code == 0
    assert src_bucket.query.call_args_list[0] == call(
        "entry-1", start=1641081601100300, stop=1643673600000000
    )


@pytest.mark.usefixtures("set_alias", "client")
def test__export_specific_entry(runner, conf, src_bucket):
    """Should export specific entry"""
    result = runner(f"-c {conf} export folder test/src_bucket . --entries=entry-2")
    assert result.exit_code == 0
    assert src_bucket.query.call_args_list == [call("entry-2", start=ANY, stop=ANY)]


@pytest.mark.usefixtures("set_alias", "client")
def test__export_multiple_specific_entry(runner, conf, src_bucket):
    """Should export multiple specific entries"""
    result = runner(
        f"-c {conf} export folder test/src_bucket . --entries=entry-2,entry-1"
    )
    assert result.exit_code == 0
    assert src_bucket.query.call_args_list == [
        call("entry-1", start=ANY, stop=ANY),
        call("entry-2", start=ANY, stop=ANY),
    ]
