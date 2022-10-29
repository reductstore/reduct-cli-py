"""Unit tests for bucket commands"""
import pytest
from reduct import BucketInfo, Client
from rich.console import Console
from rich.table import Table


@pytest.fixture(name="console")
def _patch_console(mocker) -> Console:
    table_kls = mocker.patch("reduct_cli.bucket.Table")
    table_kls.return_value = mocker.Mock(spec=Table)

    console = mocker.patch("reduct_cli.bucket.console")
    return console


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


@pytest.mark.usefixtures("set_alias", "client")
def test__get_short_list(runner, conf):
    """Should print list of buckets"""

    result = runner(f"-c {conf} bucket ls test")
    assert result.exit_code == 0
    assert result.output.split("\n") == ["bucket-1", "bucket-2", ""]


@pytest.mark.usefixtures("set_alias", "client")
def test__get_full_list(runner, conf, console):
    """Should print buckets as a table with full information"""

    result = runner(f"-c {conf} bucket ls --full test")
    assert result.exit_code == 0

    table = console.print.call_args[0][0]
    # Check headers
    assert [call[0][0] for call in table.add_column.call_args_list] == [
        "Name",
        "Entry Count",
        "Size",
        "Oldest Record",
        "Latest Record",
    ]
    # Check data
    assert [call[0] for call in table.add_row.call_args_list] == [
        ("bucket-1", "1", "1 MB", "1970-01-01T01:16:40", "1970-01-01T02:23:20"),
        ("bucket-2", "5", "50 KB", "1970-01-01T02:40:00", "1970-01-01T03:13:20"),
        (
            "Total for 2 buckets",
            "6",
            "1 MB",
            "1970-01-01T01:16:40",
            "1970-01-01T03:13:20",
        ),
    ]


@pytest.mark.usefixtures("set_alias")
def test__get_error(runner, conf, client):
    """Should print error if something got wrong"""
    client.list.side_effect = RuntimeError("Oops")
    result = runner(f"-c {conf} bucket ls test")
    assert result.exit_code == 0
    assert result.output == "Status: Error\nOops\n"
