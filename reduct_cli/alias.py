"""Alias commands"""
import click
from click import Abort

from reduct_cli.config import Config, read_config, write_config, Alias
from reduct_cli.consoles import console, error_console


@click.group()
def alias():
    """Commands to manage aliases"""


@alias.command()
@click.pass_context
def show(ctx):
    """Show configured aliases"""
    conf = read_config(ctx.obj["config_path"])
    console.print_json(data=conf["aliases"])


@alias.command()
@click.argument("name")
@click.pass_context
def add(ctx, name: str):
    """Add a new alias with NAME"""
    conf: Config = read_config(ctx.obj["config_path"])
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
def remove(ctx, name: str):
    """
    Remove alias with NAME
    """
    # Check if name exists
    conf: Config = read_config(ctx.obj["config_path"])
    if name not in conf["aliases"]:
        error_console.print(f"Alias '{name}' doesn't exist")
        raise Abort()

    conf["aliases"].pop(name)
    write_config(ctx.obj["config_path"], conf)
