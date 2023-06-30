"""Unit tests for bucket commands"""

import pytest
from reduct import BucketInfo, Client, Bucket, BucketSettings, QuotaType, EntryInfo
from rich.console import Console
from rich.table import Table


@pytest.fixture(name="console")
def _patch_console(mocker) -> Console:
    table_kls = mocker.patch("reduct_cli.bucket.Table")
    table_kls.return_value = mocker.Mock(spec=Table)

    console = mocker.patch("reduct_cli.bucket.console")
    return console


@pytest.fixture(name="bucket")
def _make_bucket(mocker) -> Bucket:
    bucket = mocker.Mock(spec=Bucket)
    bucket.name = "bucket-1"
    bucket.info.return_value = BucketInfo(
        name="bucket-1",
        entry_count=1,
        size=1050000,
        oldest_record=1000000000,
        latest_record=5000000000,
    )
    bucket.get_settings.return_value = BucketSettings(
        quota_type=QuotaType.FIFO,
        quota_size=10 * 12,
        max_block_size=10 * 5,
        max_block_records=199,
    )

    bucket.get_entry_list.return_value = [
        EntryInfo(
            name="entry-1",
            size=1050000,
            block_count=100,
            record_count=10000,
            oldest_record=1000000000,
            latest_record=5000000000,
        )
    ]

    return bucket


@pytest.fixture(name="build_client_func")
def _build_client(mocker) -> Client:
    return mocker.patch("reduct_cli.bucket.build_client")


@pytest.fixture(name="client")
def _make_client(mocker, bucket, build_client_func) -> Client:
    build_client_func.return_value = mocker.Mock(spec=Client)
    build_client_func.return_value.list.return_value = [
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

    build_client_func.return_value.get_bucket.return_value = bucket
    return build_client_func.return_value


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
        "Oldest Record (UTC)",
        "Latest Record (UTC)",
    ]
    # Check data
    assert [call[0] for call in table.add_row.call_args_list] == [
        ("bucket-1", "1", "1 MB", "1970-01-01T00:16:40", "1970-01-01T01:23:20"),
        ("bucket-2", "5", "50 KB", "1970-01-01T01:40:00", "1970-01-01T02:13:20"),
        (
            "Total for 2 buckets",
            "6",
            "1 MB",
            "1970-01-01T00:16:40",
            "1970-01-01T02:13:20",
        ),
    ]


@pytest.mark.usefixtures("set_alias")
def test__get_error(runner, conf, client):
    """Should print error if something got wrong"""
    client.list.side_effect = RuntimeError("Oops")
    result = runner(f"-c {conf} bucket ls test")
    assert result.output == "[RuntimeError] Oops\nAborted!\n"
    assert result.exit_code == 1


@pytest.mark.usefixtures("set_alias", "client")
def test__show_bucket(runner, conf):
    """Should show bucket's info"""

    result = runner(f"-c {conf} bucket show test/bucket-1")
    assert result.output.split("\n") == [
        "Entry count:         1",
        "Size:                1 MB",
        "Oldest Record (UTC): 1970-01-01T00:16:40",
        "Latest Record (UTC): 1970-01-01T01:23:20",
        "History Interval:    1 hour(s)",
        "",
    ]
    assert result.exit_code == 0


@pytest.mark.usefixtures("set_alias", "client")
def test__show_full_bucket(runner, conf):
    """Should show bucket's info"""

    result = runner(f"-c {conf} bucket show --full test/bucket-1")
    assert "Entry count:         1" in result.output
    assert "Oldest Record (UTC): 1970-01-01T00:16:40" in result.output
    assert "Latest Record (UTC): 1970-01-01T01:23:20" in result.output
    assert "History Interval:    1 hour(s)" in result.output

    assert "Quota Type:         FIFO" in result.output
    assert "Quota Size:         120 B" in result.output
    assert "Max. Block Size:    50 B" in result.output
    assert "Max. Block Records: 199" in result.output

    assert "entry-1" in result.output
    assert result.exit_code == 0


@pytest.mark.usefixtures("set_alias")
def test__show_error(runner, conf, client):
    """Should print error if something got wrong"""
    client.get_bucket.side_effect = RuntimeError("Oops")
    result = runner(f"-c {conf} bucket show test/bucket-1")
    assert result.exit_code == 1
    assert result.output == "[RuntimeError] Oops\nAborted!\n"


@pytest.mark.usefixtures("set_alias")
def test__create_bucket_default(runner, conf, client, build_client_func):
    """Should create a bucket with default settings"""
    result = runner(f"-c {conf} bucket create test/bucket-1")
    assert result.output == "Bucket 'bucket-1' created\n"
    assert result.exit_code == 0

    client.create_bucket.assert_called_with("bucket-1", BucketSettings())
    build_client_func.assert_called_with(conf, "test", 60)


@pytest.mark.usefixtures("set_alias")
def test__create_bucket_settings(runner, conf, client):
    """Should create a bucket with settings"""
    result = runner(
        f"-c {conf} bucket create "
        f"--quota-type FIFO --quota-size 100Gb --block-size 19Mb --block-records 100 test/bucket-1"
    )
    assert result.output == "Bucket 'bucket-1' created\n"
    assert result.exit_code == 0

    client.create_bucket.assert_called_with(
        "bucket-1",
        BucketSettings(
            quota_type=QuotaType.FIFO,
            quota_size=100000000000,
            max_block_size=19000000,
            max_block_records=100,
        ),
    )


@pytest.mark.usefixtures("set_alias")
def test__create_error(runner, conf, client):
    """Should print error if something got wrong"""
    client.create_bucket.side_effect = RuntimeError("Oops")
    result = runner(f"-c {conf} bucket create test/bucket-1")
    assert result.output == "[RuntimeError] Oops\nAborted!\n"
    assert result.exit_code == 1


@pytest.mark.usefixtures("set_alias")
def test__create_error_size(runner, conf, client):
    """Should print error if size is invalid"""
    result = runner(f"-c {conf} bucket create -s 100XX test/bucket-1")
    assert result.output == "[ValueError] Failed to parse 100XX\nAborted!\n"
    assert result.exit_code == 1

    client.create_bucket.assert_not_called()


@pytest.mark.usefixtures("set_alias", "client")
def test__create_update_settings(runner, conf, bucket):
    """Should update settings of a bucket"""
    result = runner(
        f"-c {conf} bucket update "
        f"--quota-type FIFO --quota-size 100Gb --block-size 19Mb --block-records 100 test/bucket-1"
    )
    assert result.output == "Bucket 'bucket-1' was updated\n"
    assert result.exit_code == 0

    bucket.set_settings.assert_called_with(
        BucketSettings(
            quota_type=QuotaType.FIFO,
            quota_size=100000000000,
            max_block_size=19000000,
            max_block_records=100,
        ),
    )


@pytest.mark.usefixtures("set_alias", "client")
def test__update_error(runner, conf, bucket):
    """Should print error if something got wrong"""
    bucket.set_settings.side_effect = RuntimeError("Oops")
    result = runner(f"-c {conf} bucket update test/bucket-1")
    assert result.output == "[RuntimeError] Oops\nAborted!\n"
    assert result.exit_code == 1


@pytest.mark.usefixtures("set_alias", "client")
def test__remove(runner, conf, bucket):
    """Should remove a bucket"""
    result = runner(f"-c {conf} bucket rm test/bucket-1", input="Y\n")
    assert result.output == (
        "All data in bucket 'bucket-1' will be REMOVED.\n"
        "Do you want to continue? [y/N]: Y\n"
        "Bucket 'bucket-1' was removed\n"
    )
    assert result.exit_code == 0

    bucket.remove.assert_called_once()


@pytest.mark.usefixtures("set_alias", "client")
def test__remove_canceled(runner, conf, bucket):
    """Should cancel removing a bucket"""
    result = runner(f"-c {conf} bucket rm test/bucket-1", input="N\n")
    assert result.output == (
        "All data in bucket 'bucket-1' will be REMOVED.\n"
        "Do you want to continue? [y/N]: N\n"
        "Canceled\n"
    )
    assert result.exit_code == 0

    bucket.remove.assert_not_called()


@pytest.mark.usefixtures("set_alias", "client")
def test__remove_error(runner, conf, bucket):
    """Should print error if something got wrong"""
    bucket.remove.side_effect = RuntimeError("Oops")
    result = runner(f"-c {conf} bucket rm test/bucket-1", input="Y\n")
    assert result.output == (
        "All data in bucket 'bucket-1' will be REMOVED.\n"
        "Do you want to continue? [y/N]: Y\n"
        "[RuntimeError] Oops\n"
        "Aborted!\n"
    )
    assert result.exit_code == 1
