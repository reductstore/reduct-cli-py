"""Alias commands"""
from pathlib import Path
from typing import Optional

import click
from click import Abort

from reduct_cli.config import Config, read_config, write_config, Alias
from reduct_cli.consoles import console, error_console


def get_alias(config_path: Path, name: str) -> Alias:
    """Helper method to parse alias from config"""
    conf = read_config(config_path)

    if name not in conf["aliases"]:
        error_console.print(f"Alias '{name}' doesn't exist")
        raise Abort()
    alias_: Alias = conf["aliases"][name]
    return alias_


@click.group()
@click.pass_context
def alias_cmd(ctx):
    """Commands to manage aliases"""
    ctx.obj["conf"] = read_config(ctx.obj["config_path"])


@alias_cmd.command()
@click.pass_context
def ls(ctx):
    """Print list of aliases"""
    for name, _ in ctx.obj["conf"]["aliases"].items():
        console.print(name)


@alias_cmd.command()
@click.argument("name")
@click.option("--token/--no-token", "-t", help="Show token", default=False)
@click.pass_context
def show(ctx, name: str, token: bool):
    """Show alias configuration"""
    alias_: Alias = get_alias(ctx.obj["config_path"], name)
    console.print(f"[bold]URL[/bold]:\t\t{alias_['url']}")
    if token:
        console.print(f"[bold]Token[/bold]:\t\t{alias_['token']}")


@alias_cmd.command()
@click.argument("name")
@click.option("--url", "-L", help="Server URL")
@click.option("--token", "-t", help="API token")
@click.pass_context
def add(ctx, name: str, url: Optional[str], token: Optional[str]):
    """Add a new alias with NAME"""
    conf: Config = ctx.obj["conf"]
    if name in conf["aliases"]:
        error_console.print(f"Alias '{name}' already exists")
        raise Abort()

    if url is None or len(url) == 0:
        url = click.prompt("URL", type=str)
    if token is None:
        token = click.prompt("API Token", type=str, default="")

    entry: Alias = dict(url=url, token=token)

    conf["aliases"][name] = entry
    write_config(ctx.obj["config_path"], conf)


@alias_cmd.command()
@click.argument("name")
@click.pass_context
def rm(ctx, name: str):
    """
    Remove alias with NAME
    """
    # Check if name exists
    conf: Config = ctx.obj["conf"]
    _ = get_alias(ctx.obj["config_path"], name)

    conf["aliases"].pop(name)
    write_config(ctx.obj["config_path"], conf)
