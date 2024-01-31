"""Unit tests for replication commands"""

import pytest
from reduct import ReplicationInfo, Client, ReplicationDetailInfo, ReplicationSettings
from reduct.client import (
    ReplicationDiagnostics,
    ReplicationDiagnosticsDetail,
    ReplicationDiagnosticsError,
)
from rich.console import Console
from rich.table import Table


@pytest.fixture(name="console")
def _patch_console(mocker) -> Console:
    table_kls = mocker.patch("reduct_cli.bucket.Table")
    table_kls.return_value = mocker.Mock(spec=Table)

    console = mocker.patch("reduct_cli.bucket.console")
    return console


@pytest.fixture(name="client")
def _make_client(mocker, replication_info) -> Client:
    client = mocker.Mock(spec=Client)
    client.get_replications.return_value = [replication_info]

    kls = mocker.patch("reduct_cli.replication.build_client")
    kls.return_value = client
    return client


@pytest.fixture(name="replication_info")
def _make_replication_info(mocker) -> ReplicationInfo:
    replication_info = ReplicationInfo(
        name="test",
        is_active=True,
        is_provisioned=True,
        pending_records=0,
    )
    return replication_info


@pytest.fixture(name="replication_detail_info")
def _make_detail_info(replication_info) -> ReplicationDetailInfo:
    detail_info = ReplicationDetailInfo(
        info=replication_info,
        settings=ReplicationSettings(
            src_bucket="src_bucket",
            dst_bucket="dst_bucket",
            dst_host="http://test",
        ),
        diagnostics=ReplicationDiagnostics(
            hourly=ReplicationDiagnosticsDetail(
                ok=0,
                errored=0,
                errors={
                    400: ReplicationDiagnosticsError(
                        count=10,
                        last_message="Bad request",
                    )
                },
            ),
        ),
    )
    return detail_info


@pytest.mark.usefixtures("set_alias")
def test_ls(
    runner,
    conf,
    console,
    client,
):
    """Test ls command"""
    result = runner(f"-c {conf} replication ls test")
    assert result.exit_code == 0
    assert result.output == "test\n"
    client.get_replications.assert_called_once_with()


@pytest.mark.usefixtures("set_alias")
def test_ls_error(
    runner,
    conf,
    console,
    client,
):
    """Test ls command"""
    client.get_replications.side_effect = RuntimeError("Oops")
    result = runner(f"-c {conf} replication ls test")
    assert result.exit_code == 1
    assert result.output == ("[RuntimeError] Oops\n" "Aborted!\n")


@pytest.mark.usefixtures("set_alias")
def test_ls_full(runner, conf, console, client):
    """Test ls command with full option"""
    result = runner(f"-c {conf} replication ls --full test")
    assert result.exit_code == 0
    assert result.output == (
        (
            "┏━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┓\n"
            "┃ Name ┃ Active ┃ Provisioned ┃ Pending Records ┃\n"
            "┡━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━┩\n"
            "│ test │ True   │ True        │ 0               │\n"
            "└──────┴────────┴─────────────┴─────────────────┘\n"
        )
    )

    client.get_replications.assert_called_once_with()


@pytest.mark.usefixtures("set_alias")
def test_show(runner, conf, console, client, replication_detail_info):
    """Test show command"""
    client.get_replication_detail.return_value = replication_detail_info
    result = runner(f"-c {conf} replication show test test")
    assert result.exit_code == 0
    assert result.output.startswith(
        "╭─────────────── State ────────────────╮╭────────────── Settings ──────────────╮\n"
        "│ Name:                         test   ││ Source Bucket:         src_bucket    │\n"
        "│ Active:                       True   ││ Destination Bucket:    dst_bucket    │\n"
        "│ Provisioned:                  True   ││ Destination Server:    http://test   │\n"
        "│ Pending Records:              0      ││ Entries:               []            │\n"
        "│ Synced Records in hour:       0      ││ Include:               {}            │\n"
        "│ Errored Records in hour:      0      ││ Exclude:               {}            │\n"
        "╰──────────────────────────────────────╯╰──────────────────────────────────────╯\n"
        "                                Errors last hour                                \n"
        "┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
        "┃                 Error Code ┃ Count          ┃ Last Message                   ┃\n"
        "┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩\n"
        "│                        400 │ 10             │ Bad request                    │\n"
        "└────────────────────────────┴────────────────┴────────────────────────────────┘\n"
    )


@pytest.mark.usefixtures("set_alias")
def test_show_error(runner, conf, console, client, replication_detail_info):
    """Test show command"""
    client.get_replication_detail.side_effect = RuntimeError("Oops")
    result = runner(f"-c {conf} replication show test test")
    assert result.exit_code == 1
    assert result.output == ("[RuntimeError] Oops\n" "Aborted!\n")


@pytest.mark.usefixtures("set_alias")
def test_create(runner, conf, console, client, replication_detail_info):
    """Test create command"""
    result = runner(
        f"-c {conf} replication create test test src_bucket dst_bucket http://test"
        f" -T token "
        f"--entries entry-1,entry-2 "
        f"--include key1=value1,key2=value2 "
        f"--exclude key3=value3,key4=value4"
    )
    assert result.exit_code == 0
    assert result.output == ("New replication 'test' created\n")

    client.create_replication.assert_called_once_with(
        "test",
        ReplicationSettings(
            src_bucket="src_bucket",
            dst_bucket="dst_bucket",
            dst_host="http://test",
            dst_token="token",
            entries=["entry-1", "entry-2"],
            include={"key1": "value1", "key2": "value2"},
            exclude={"key3": "value3", "key4": "value4"},
        ),
    )


@pytest.mark.usefixtures("set_alias")
def test_create_default(runner, conf, console, client, replication_detail_info):
    """Test create command"""
    result = runner(
        f"-c {conf} replication create test test src_bucket dst_bucket http://test"
    )
    assert result.exit_code == 0
    assert result.output == ("New replication 'test' created\n")

    client.create_replication.assert_called_once_with(
        "test",
        ReplicationSettings(
            src_bucket="src_bucket",
            dst_bucket="dst_bucket",
            dst_host="http://test",
            dst_token="",
            entries=[],
            include={},
            exclude={},
        ),
    )


@pytest.mark.usefixtures("set_alias")
def test_create_error(runner, conf, console, client, replication_detail_info):
    """Test create command"""
    client.create_replication.side_effect = RuntimeError("Oops")
    result = runner(
        f"-c {conf} replication create test test src_bucket dst_bucket http://test"
    )
    assert result.exit_code == 1
    assert result.output == ("[RuntimeError] Oops\n" "Aborted!\n")


@pytest.mark.usefixtures("set_alias")
def test_update(runner, conf, console, client, replication_detail_info):
    """Test update command"""
    result = runner(
        f"-c {conf} replication update test test src_bucket dst_bucket http://test"
        f" -T token "
        f"--entries entry-1,entry-2 "
        f"--include key1=value1,key2=value2 "
        f"--exclude key3=value3,key4=value4"
    )
    assert result.exit_code == 0
    assert result.output == ("Replication 'test' updated\n")

    client.update_replication.assert_called_once_with(
        "test",
        ReplicationSettings(
            src_bucket="src_bucket",
            dst_bucket="dst_bucket",
            dst_host="http://test",
            dst_token="token",
            entries=["entry-1", "entry-2"],
            include={"key1": "value1", "key2": "value2"},
            exclude={"key3": "value3", "key4": "value4"},
        ),
    )


@pytest.mark.usefixtures("set_alias")
def test_update_default(runner, conf, console, client, replication_detail_info):
    """Test update command"""
    result = runner(
        f"-c {conf} replication update test test src_bucket dst_bucket http://test"
    )
    assert result.exit_code == 0
    assert result.output == ("Replication 'test' updated\n")

    client.update_replication.assert_called_once_with(
        "test",
        ReplicationSettings(
            src_bucket="src_bucket",
            dst_bucket="dst_bucket",
            dst_host="http://test",
            dst_token="",
            entries=[],
            include={},
            exclude={},
        ),
    )


@pytest.mark.usefixtures("set_alias")
def test_update_error(runner, conf, console, client, replication_detail_info):
    """Test update command"""
    client.update_replication.side_effect = RuntimeError("Oops")
    result = runner(
        f"-c {conf} replication update test test src_bucket dst_bucket http://test"
    )
    assert result.exit_code == 1
    assert result.output == ("[RuntimeError] Oops\n" "Aborted!\n")


@pytest.mark.usefixtures("set_alias")
def test_delete(runner, conf, console, client, replication_detail_info):
    """Test delete command"""
    result = runner(f"-c {conf} replication rm test test")
    assert result.exit_code == 0
    assert result.output == ("Replication 'test' deleted\n")

    client.delete_replication.assert_called_once_with("test")


@pytest.mark.usefixtures("set_alias")
def test_delete_error(runner, conf, console, client, replication_detail_info):
    """Test delete command"""
    client.delete_replication.side_effect = RuntimeError("Oops")
    result = runner(f"-c {conf} replication rm test test")
    assert result.exit_code == 1
    assert result.output == ("[RuntimeError] Oops\n" "Aborted!\n")
