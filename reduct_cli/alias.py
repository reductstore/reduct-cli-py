"""Alias commands"""
from typing import Optional

import click
from click import Abort
from reduct_cli.utils.error import error_handle

from reduct_cli.config import Config, read_config, write_config, Alias
from reduct_cli.utils.consoles import console, error_console
from reduct_cli.utils.helpers import get_alias


@click.group()
@click.pass_context
def alias(ctx):
    """Commands to manage aliases"""
    ctx.obj["conf"] = read_config(ctx.obj["config_path"])


@alias.command()
@click.pass_context
def ls(ctx):
    """Print list of aliases"""
    for name, _ in ctx.obj["conf"]["aliases"].items():
        console.print(name)


@alias.command()
@click.argument("name")
@click.option("--token/--no-token", "-t", help="Show token", default=False)
@click.pass_context
def show(ctx, name: str, token: bool):
    """Show alias configuration"""
    alias_: Alias = get_alias(ctx.obj["config_path"], name)
    console.print(f"[bold]URL[/bold]:\t\t{alias_['url']}")
    if token:
        console.print(f"[bold]Token[/bold]:\t\t{alias_['token']}")


@alias.command()
@click.argument("name")
@click.option(
    "--url", "-L", help="Server URL must be in format http(s)://example.com[:port]"
)
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

    with error_handle():
        entry = Alias(url=url, token=token).dict()

        conf["aliases"][name] = entry
        write_config(ctx.obj["config_path"], conf)


@alias.command()
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
