"""Replication commands"""
from asyncio import new_event_loop as loop
from typing import List

import click
from reduct import ReplicationSettings
from reduct.client import ReplicationInfo, ReplicationDetailInfo
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table

from reduct_cli.export import entries_option, include_option, exclude_option
from reduct_cli.utils.consoles import console
from reduct_cli.utils.error import error_handle
from reduct_cli.utils.helpers import build_client, extract_key_values

run = loop().run_until_complete


@click.group()
def replication():
    """Commands to manage and monitor replications"""


@replication.command()
@click.argument("alias")
@click.option("--full/--no-full", help="Print full information", default=False)
@click.pass_context
def ls(ctx, alias: str, full: bool):
    """Print list of tokens

    ALIAS is the name of the alias to use. See 'reduct alias' for more information.
    """
    client = build_client(ctx.obj["config_path"], alias, timeout=ctx.obj["timeout"])
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
    """Show replication

    Show detailed information about replication with NAME.on ALIAS.
    """
    client = build_client(ctx.obj["config_path"], alias, timeout=ctx.obj["timeout"])

    with error_handle():
        repl: ReplicationDetailInfo = run(client.get_replication_detail(name))

        info_text = "\n".join(
            [
                f"Name:                         {repl.info.name}",
                f"Active:                       {repl.info.is_active}",
                f"Provisioned:                  {repl.info.is_provisioned}",
                f"Pending Records:              {repl.info.pending_records}",
                f"Synced Records in hour:       {repl.diagnostics.hourly.ok}",
                f"Errored Records in hour:      {repl.diagnostics.hourly.errored}",
            ]
        )

        settings_text = "\n".join(
            [
                f"Source Bucket:         {repl.settings.src_bucket}",
                f"Destination Bucket:    {repl.settings.dst_bucket}",
                f"Destination Server:    {repl.settings.dst_host}",
                f"Entries:               {repl.settings.entries}",
                f"Include:               {repl.settings.include}",
                f"Exclude:               {repl.settings.exclude}",
            ]
        )

        table = Table(expand=True, title="Errors last hour")
        table.add_column("Error Code", justify="right", style="red")
        table.add_column("Count")
        table.add_column("Last Message", style="yellow")
        for code, item in repl.diagnostics.hourly.errors.items():
            table.add_row(str(code), str(item.count), item.last_message)

        layout = Layout()
        layout.split_column(Layout(name="upper", size=8), Layout(table))
        layout["upper"].split_row(
            Layout(Panel(info_text, title="State")),
            Layout(Panel(settings_text, title="Settings")),
        )
        console.print(layout)


@replication.command()
@click.argument("alias")
@click.argument("name")
@click.argument("src-bucket")
@click.argument("dst-bucket")
@click.argument("dst-host")
@click.option("--dst-token", "-T", help="Destination token", default="")
@entries_option
@include_option
@exclude_option
@click.pass_context
def create(
    ctx,
    alias: str,
    name: str,
    src_bucket: str,
    dst_bucket: str,
    dst_host: str,
    dst_token: str,
    entries: str,
    include: str,
    exclude: str,
):  # pylint: disable=too-many-arguments
    """Create replication

    The command creates a new replication with NAME which copies data
    from SRC_BUCKET on ALIAS to DST_BUCKET on DST_HOST.
    SRC_BUCKET and DST_BUCKET should be created beforehand.
    DST_HOST is URL of the destination server.
    """
    client = build_client(ctx.obj["config_path"], alias, timeout=ctx.obj["timeout"])
    with error_handle():
        settings = ReplicationSettings(
            src_bucket=src_bucket,
            dst_bucket=dst_bucket,
            dst_host=dst_host,
            dst_token=dst_token,
            entries=entries.split(",") if entries else [],
            include=extract_key_values(include.split(",")),
            exclude=extract_key_values(exclude.split(",")),
        )

        run(client.create_replication(name, settings))
        console.print(f"New replication '{name}' created")


@replication.command()
@click.argument("alias")
@click.argument("name")
@click.argument("src-bucket")
@click.argument("dst-bucket")
@click.argument("dst-host")
@click.option("--dst-token", "-T", help="Destination token", default="")
@entries_option
@include_option
@exclude_option
@click.pass_context
def update(
    ctx,
    alias: str,
    name: str,
    src_bucket: str,
    dst_bucket: str,
    dst_host: str,
    dst_token: str,
    entries: str,
    include: str,
    exclude: str,
):  # pylint: disable=too-many-arguments
    """Update replication

    The command updates replication with NAME which copies
    data from SRC_BUCKET on ALIAS to DST_BUCKET on DST_HOST.
    SRC_BUCKET and DST_BUCKET should be created beforehand.
    DST_HOST is URL of the destination server.
    """
    client = build_client(ctx.obj["config_path"], alias, timeout=ctx.obj["timeout"])
    with error_handle():
        settings = ReplicationSettings(
            src_bucket=src_bucket,
            dst_bucket=dst_bucket,
            dst_host=dst_host,
            dst_token=dst_token,
            entries=entries.split(",") if entries else [],
            include=extract_key_values(include.split(",")),
            exclude=extract_key_values(exclude.split(",")),
        )

        run(client.update_replication(name, settings))
        console.print(f"Replication '{name}' updated")


@replication.command()
@click.argument("alias")
@click.argument("name")
@click.pass_context
def rm(ctx, alias: str, name: str):
    """Remove replication

    Remove replication with NAME on ALIAS.
    """
    client = build_client(ctx.obj["config_path"], alias, timeout=ctx.obj["timeout"])
    with error_handle():
        run(client.delete_replication(name))
        console.print(f"Replication '{name}' deleted")
