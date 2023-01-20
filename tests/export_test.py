"""Unit tests for export command"""
from pathlib import Path
from tempfile import gettempdir

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
    assert "Entry 'entry-1' (copied 6 B" in result.output
    assert result.exit_code == 0

    src_bucket.query.assert_called_with(
        "entry-1", start=1641074401100300, stop=1643666400000000
    )

    assert (
        path / "src_bucket" / "entry-1" / f"{records[0].timestamp}.bin"
    ).read_bytes() == b"Hey"
    assert (
        path / "src_bucket" / "entry-1" / f"{records[1].timestamp}.bin"
    ).read_bytes() == b"Bye"


@pytest.mark.usefixtures("set_alias", "client")
def test__export_to_folder_ok_without_interval(runner, conf, src_bucket, records):
    """Should export a bucket to a fodder one without time interval"""
    path = Path(gettempdir()) / "reduct-test"
    result = runner(f"-c {conf} export folder test/src_bucket {path}")
    assert "Entry 'entry-1' (copied 6 B" in result.output
    assert result.exit_code == 0

    src_bucket.query.assert_called_with("entry-1", start=1000000000, stop=5000000000)

    assert (
        path / "src_bucket" / "entry-1" / f"{records[0].timestamp}.bin"
    ).read_bytes() == b"Hey"
    assert (
        path / "src_bucket" / "entry-1" / f"{records[1].timestamp}.bin"
    ).read_bytes() == b"Bye"


@pytest.mark.usefixtures("set_alias")
def test__export_to_folder_fail(runner, client, conf):
    """Should fail if the destination folder does not exist"""
    client.get_bucket.side_effect = RuntimeError("Oops")

    result = runner(f"-c {conf} export folder test/src_bucket .")
    assert result.output == "[RuntimeError] Oops\nAborted!\n"
    assert result.exit_code == 1


@pytest.mark.usefixtures("set_alias", "client")
def test__export_utc_timestamp(runner, conf, dest_bucket, src_bucket):
    """Should support Z designator for UTC timestamps"""
    result = runner(
        f"-c {conf} export folder test/src_bucket . --start 2022-01-02T00:00:01.100300Z --stop 2022-02-01T00:00:00Z"
    )
    assert result.exit_code == 0
    src_bucket.query.assert_called_with(
        "entry-1", start=1641081601100300, stop=1643673600000000
    )
