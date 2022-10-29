"""Common fixtures"""
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


@pytest.fixture(name="url")
def _make_url() -> str:
    return "http://127.0.0.1:8383"


@pytest.fixture(name="set_alias")
def _set_alias(runner, conf, url):
    runner(f"-c {conf} alias add test", input=f"{url}\ntoken\n")
