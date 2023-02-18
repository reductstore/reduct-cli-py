"""Unit tests for token commands"""
from datetime import datetime

import pytest
from reduct import Client, FullTokenInfo, Permissions, Token


@pytest.fixture(name="client")
def _make_client(mocker) -> Client:
    kls = mocker.patch("reduct_cli.token.build_client")
    kls.return_value = mocker.Mock(spec=Client)
    return kls.return_value


@pytest.mark.usefixtures("set_alias")
def test__get_token_list(runner, conf, client):
    """Should print list of tokens"""
    client.get_token_list.return_value = [
        Token(name="token-1", created_at=datetime(2020, 1, 1, 0, 0, 0)),
        Token(name="token-2", created_at=datetime(2020, 1, 1, 0, 0, 0)),
    ]
    result = runner(f"-c {conf} token ls test")
    assert result.output.split("\n") == ["token-1", "token-2", ""]
    assert result.exit_code == 0


@pytest.mark.usefixtures("set_alias")
def test__get_token_list_error(runner, conf, client):
    """Should print error if something got wrong"""
    client.get_token_list.side_effect = RuntimeError("Oops")
    result = runner(f"-c {conf} token ls test")
    assert result.exit_code == 1
    assert result.output == "[RuntimeError] Oops\nAborted!\n"


@pytest.mark.usefixtures("set_alias")
def test__get_token_info(runner, conf, client):
    """Should print information about token"""
    client.get_token.return_value = FullTokenInfo(
        name="test-token",
        created_at=datetime(2020, 1, 1, 0, 0, 0),
        permissions=Permissions(
            full_access=True, read=["bucket-1"], write=["bucket-2"]
        ),
    )

    result = runner(f"-c {conf} token show test test-token")
    assert result.output.split("\n") == [
        "Name:    test-token",
        "Created At:     2020-01-01 00:00:00",
        "Full Access:    True",
        "Read Only:      ['bucket-1']",
        "Write Only:     ['bucket-2']",
        "",
    ]
    assert result.exit_code == 0


@pytest.mark.usefixtures("set_alias")
def test__get_token_error(runner, conf, client):
    """Should print error if something got wrong"""
    client.get_token.side_effect = RuntimeError("Oops")
    result = runner(f"-c {conf} token show test test-token")
    assert result.exit_code == 1
    assert result.output == "[RuntimeError] Oops\nAborted!\n"


@pytest.mark.usefixtures("set_alias")
def test__create_token(runner, conf, client):
    """Should create token"""
    client.create_token.return_value = "token-value"

    result = runner(
        f"-c {conf} token create test test-token --full-access"
        f" --read bucket-1,bucket-2 --write bucket-2,bucket-3"
    )
    assert result.output.split("\n") == ["New token:    token-value", ""]
    assert result.exit_code == 0
    client.create_token.assert_called_with(
        "test-token",
        Permissions(
            full_access=True,
            read=["bucket-1", "bucket-2"],
            write=["bucket-2", "bucket-3"],
        ),
    )


@pytest.mark.usefixtures("set_alias")
def test__create_token_error(runner, conf, client):
    """Should print error if something got wrong"""
    client.create_token.side_effect = RuntimeError("Oops")
    result = runner(f"-c {conf} token create test test-token")
    assert result.exit_code == 1
    assert result.output == "[RuntimeError] Oops\nAborted!\n"


@pytest.mark.usefixtures("set_alias")
def test__delete_token_with_confirm(runner, conf, client):
    """Should delete token with confirmation"""
    result = runner(f"-c {conf} token rm test test-token", input="y")
    assert result.output.split("\n") == [
        "We are going to remove token: test-token",
        "Do you want to continue? [y/N]: y",
        "Token 'test-token' was deleted",
        "",
    ]
    assert result.exit_code == 0
    client.remove_token.assert_called_with("test-token")


@pytest.mark.usefixtures("set_alias")
def test__delete_token_canceled(runner, conf, client):
    """Should cancel token deletion"""
    result = runner(f"-c {conf} token rm test test-token", input="n")
    assert result.output.split("\n") == [
        "We are going to remove token: test-token",
        "Do you want to continue? [y/N]: n",
        "Canceled",
        "",
    ]
    assert result.exit_code == 0
    client.remove_token.assert_not_called()


@pytest.mark.usefixtures("set_alias")
def test__delete_token_error(runner, conf, client):
    """Should print error if something got wrong"""
    client.remove_token.side_effect = RuntimeError("Oops")
    result = runner(f"-c {conf} token rm test test-token", input="y")
    assert result.exit_code == 1
    assert result.output.split("\n") == [
        "We are going to remove token: test-token",
        "Do you want to continue? [y/N]: y",
        "[RuntimeError] Oops",
        "Aborted!",
        "",
    ]
