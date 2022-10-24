"""Alias commands"""
from pathlib import Path

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
@click.pass_context
def add(ctx, name: str):
    """Add a new alias with NAME"""
    conf: Config = ctx.obj["conf"]
    if name in conf["aliases"]:
        error_console.print(f"Alias '{name}' already exists")
        raise Abort()

    entry: Alias = dict(
        url=click.prompt("URL", type=str),
        token=click.prompt("API Token", type=str, default=""),
    )

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
