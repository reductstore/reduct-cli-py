from asyncio import new_event_loop as loop
from typing import List

import click
from reduct import Token, Client
from reduct.client import ReplicationInfo, ReplicationDetailInfo
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table

from reduct_cli.utils.consoles import console
from reduct_cli.utils.error import error_handle
from reduct_cli.utils.helpers import build_client

run = loop().run_until_complete


@click.group()
def replication():
    """Commands to manage and monitor replications"""


@replication.command()
@click.argument("alias")
@click.option("--full/--no-full", help="Print full information", default=False)
@click.pass_context
def ls(ctx, alias: str, full: bool):
    """Print list of tokens"""
    client: Client = build_client(
        ctx.obj["config_path"], alias, timeout=ctx.obj["timeout"]
    )
    with error_handle():
        replications: List[ReplicationInfo] = run(client.get_replications())
        if not full:
            for repl in replications:
                console.print(repl.name)
        else:
            table = Table()
            table.add_column("Name", justify="right", style="green")
            table.add_column("Active")
            table.add_column("Provisioned")
            table.add_column("Pending Records", style="yellow")

            for repl in replications:
                table.add_row(
                    repl.name,
                    str(repl.is_active),
                    str(repl.is_provisioned),
                    str(repl.pending_records),
                )
            console.print(table)


@replication.command()
@click.argument("alias")
@click.argument("name")
@click.pass_context
def show(ctx, alias: str, name: str):
    """Show replication"""
    client = build_client(ctx.obj["config_path"], alias, timeout=ctx.obj["timeout"])

    with error_handle():
        replication: ReplicationDetailInfo = run(client.get_replication_detail(name))

        info_text = "\n".join(
            [
                f"Name:                         {replication.info.name}",
                f"Active:                       {replication.info.is_active}",
                f"Provisioned:                  {replication.info.is_provisioned}",
                f"Pending Records:              {replication.info.pending_records}",
                f"Synced Records in hour:       {replication.diagnostics.hourly.ok}",
                f"Errored Records in hour:      {replication.diagnostics.hourly.errored}",
            ]
        )

        settings_text = "\n".join(
            [
                f"Source Bucket:         {replication.settings.src_bucket}",
                f"Destination Bucket:    {replication.settings.dst_bucket}",
                f"Destination Server:    {replication.settings.dst_host}",
                f"Entries:               {replication.settings.entries}",
                f"Include:               {replication.settings.include}",
                f"Exclude:               {replication.settings.exclude}",
            ]
        )

        table = Table(expand=True, title="Errors last hour")
        table.add_column("Error Code", justify="right", style="red")
        table.add_column("Count")
        table.add_column("Last Message", style="yellow")
        for code, item in replication.diagnostics.hourly.errors.items():
            table.add_row(str(code), str(item.count), item.last_message)

        layout = Layout()
        layout.split_column(Layout(name="upper", size=8), Layout(table))
        layout["upper"].split_row(
            Layout(Panel(info_text, title="State")),
            Layout(Panel(settings_text, title="Settings")),
        )
        console.print(layout)
