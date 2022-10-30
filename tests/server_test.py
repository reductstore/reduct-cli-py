"""Unit tests for server commands"""
import pytest
from reduct import Client, ServerInfo, BucketSettings
from reduct.client import Defaults


@pytest.fixture(name="client")
def _make_client(mocker) -> Client:
    kls = mocker.patch("reduct_cli.server.ReductClient")
    kls.return_value = mocker.Mock(spec=Client)
    return kls.return_value


@pytest.mark.usefixtures("set_alias")
def test__get_status(runner, conf, client):
    """Should print information about server"""
    client.info.return_value = ServerInfo(
        version="1.0.0",
        uptime=900,
        usage=1024 * 1024,
        bucket_count=5,
        oldest_record=0,
        latest_record=100,
        defaults=Defaults(bucket=BucketSettings()),
    )
    result = runner(f"-c {conf} server status test")
    assert result.exit_code == 0
    assert result.output.split("\n") == [
        "Status:     Ok",
        "Version:    1.0.0",
        "Uptime:     15 minute(s)",
        "",
    ]


@pytest.mark.usefixtures("set_alias")
def test__get_error(runner, conf, client):
    """Should print error if something got wrong"""
    client.info.side_effect = RuntimeError("Oops")
    result = runner(f"-c {conf} server status test")
    assert result.exit_code == 1
    assert result.output == "[RuntimeError] Oops\nAborted!\n"
