"""Unit tests for alias command"""
import json
import time
from functools import partial
from pathlib import Path
from tempfile import gettempdir
from typing import Callable

import pytest
from click.testing import CliRunner, Result

from reduct_cli.cli import cli


@pytest.fixture(name="runner")
def _make_runner() -> Callable[[str], Result]:
    runner = CliRunner()
    return partial(runner.invoke, cli, obj={})


@pytest.fixture(name="conf")
def _make_conf() -> Path:
    return Path(gettempdir()) / str(time.time_ns() % 1000000) / "config.toml"


def test__empty_list(runner, conf):
    """Should show empty aliases"""
    result = runner(f"-c {conf} alias list")
    assert result.exit_code == 0
    assert result.output == "{}\n"


def test__add_alias_ok(runner, conf):
    """Should add an alias"""
    url = "http://127.0.0.1:8383"
    token = "token"
    result = runner(f"-c {conf} alias add storage", input=f"{url}\n{token}\n")
    assert result.exit_code == 0

    result = runner(f"-c {conf} alias show")
    assert result.exit_code == 0

    json_output = json.loads(result.output)
    json_output["storage"] = dict(url=url, token=token)


def test__add_alias_twice(runner, conf):
    """Should not add an alias if the name alread exists"""

    result = runner(
        f"-c {conf} alias add storage", input="http://127.0.0.1:8383\ntoken\n"
    )
    assert result.exit_code == 0

    result = runner(f"-c {conf} alias add storage")
    assert result.exit_code == 1
    assert result.output == "Alias 'storage' already exists\nAborted!\n"


def test__rm_ok(runner, conf):
    """Should remove alias"""
    result = runner(
        f"-c {conf} alias add storage", input="http://127.0.0.1:8383\ntoken\n"
    )
    assert result.exit_code == 0

    result = runner(f"-c {conf} alias remove storage")
    assert result.exit_code == 0

    result = runner(f"-c {conf} alias show")
    assert result.exit_code == 0
    assert result.output == "{}\n"


def test__rm_not_exist(runner, conf):
    """Shouldn't remove alias if it doesn't exist"""
    result = runner(f"-c {conf} alias remove storage")
    assert result.exit_code == 1
    assert result.output == "Alias 'storage' doesn't exist\nAborted!\n"
