import os
from importlib import metadata
from pathlib import Path
from typing import TypedDict, Dict

import click
import tomlkit as toml
from click import Abort
from rich.console import Console


class Alias(TypedDict):
    url: str
    token: str


class Config(TypedDict):
    aliases: Dict[str, Alias]


def __write_config(path: Path, config: Config):
    if not Path.exists(path):
        os.makedirs(path.parent, exist_ok=True)
    with open(path, "w") as config_file:
        config_file.write(toml.dumps(config))


def __read_config(path: Path) -> Config:
    with open(path, "r") as config_file:
        return toml.loads(config_file.read())


error_console = Console(stderr=True, style="bold red")
console = Console()


@click.group()
@click.version_option(metadata.version("reduct-cli"))
@click.pass_context
def alias(ctx):
    """CLI app"""

    config_path = Path(
        os.environ.get("CONFIG_PATH", str(Path.home() / ".reduct-cli" / "config.toml"))
    )
    if not Path.exists(config_path):
        __write_config(config_path, {"aliases": {}})

    ctx.obj["config_path"] = config_path


@alias.command()
@click.pass_context
def alias_list(ctx):
    """List configured aliases"""
    conf = __read_config(ctx.obj["config_path"])
    console.print_json(data=conf["aliases"])


@alias.command()
@click.argument("name")
@click.pass_context
def alias_add(ctx, name: str):
    """Add a new alias with NAME"""
    conf: Config = __read_config(ctx.obj["config_path"])
    if name in conf["aliases"]:
        error_console.print(f"Alias '{name}' already exists")
        raise Abort()

    entry: Alias = dict(
        url=click.prompt("URL", type=str),
        token=click.prompt("API Token", type=str, default=""),
    )

    conf["aliases"][name] = entry
    __write_config(ctx.obj["config_path"], conf)


@alias.command()
@click.argument("name")
@click.pass_context
def alias_rm(ctx, name: str):
    """
    Remove alias by NAME
    """
    # Check if name exists
    conf: Config = __read_config(ctx.obj["config_path"])
    if name not in conf["aliases"]:
        error_console.print(f"Alias '{name}' doesn't exists")
        raise Abort()

    conf["aliases"].pop(name)
    __write_config(ctx.obj["config_path"], conf)
