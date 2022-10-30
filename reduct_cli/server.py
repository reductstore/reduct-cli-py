"""Server commands"""
from asyncio import new_event_loop as loop

import click
from reduct import Client as ReductClient, ServerInfo

from reduct_cli.alias import get_alias
from reduct_cli.consoles import console
from reduct_cli.error import error_handle
from reduct_cli.humanize import pretty_time_interval

run = loop().run_until_complete


@click.group()
def server_cmd():
    """Commands to manage server"""


@server_cmd.command()
@click.argument("alias")
@click.pass_context
def status(ctx, alias: str):
    """
    Connect to server with alias and print its status
    """
    alias = get_alias(ctx.obj["config_path"], alias)
    client = ReductClient(
        alias["url"], api_token=alias["token"], timeout=ctx.obj["timeout"]
    )

    with error_handle():
        info: ServerInfo = run(client.info())

        console.print("Status:     [green]Ok[/green]")
        console.print(f"Version:    {info.version}")
        console.print(f"Uptime:     {pretty_time_interval(info.uptime)}")
