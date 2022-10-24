"""Server commands"""
from asyncio import new_event_loop as loop

import click
from reduct import Client as ReductClient, ServerInfo

from reduct_cli.humanize import time_interval, data_size
from reduct_cli.alias import get_alias
from reduct_cli.consoles import console, error_console

run = loop().run_until_complete


@click.group()
def server():
    """Commands to manage server"""


@server.command()
@click.argument("alias")
@click.pass_context
def status(ctx, alias: str):
    """
    Connect to server with alias and print its status
    """
    alias = get_alias(ctx.obj["config_path"], alias)
    client = ReductClient(alias["url"], api_token=alias["token"])

    try:
        info: ServerInfo = run(client.info())
        console.print("Status: [green]Ok[/green]")
        console.print(f"Version: {info.version}")
        console.print(f"Uptime: {time_interval(info.uptime)}")
        console.print(f"Usage: {data_size(info.usage)}")
        console.print(f"Buckets: {info.bucket_count}")

    except Exception as err:  # pylint: disable=broad-except
        console.print("Status: [red]Error[/red]")
        error_console.print(err)
