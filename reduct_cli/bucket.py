"""Bucket commands"""
from asyncio import new_event_loop as loop
from datetime import datetime
from typing import List

import click
from reduct import Client as ReductClient, BucketInfo
from rich.table import Table

from reduct_cli.alias import get_alias
from reduct_cli.consoles import console, error_console
from reduct_cli.humanize import data_size

run = loop().run_until_complete


@click.group()
def bucket():
    """Commands to manage buckets"""


@bucket.command()
@click.argument("alias")
@click.option("--full/--no-full", help="Print full information", default=False)
@click.pass_context
def ls(ctx, alias: str, full: bool):
    """
    List buckets
    """
    alias = get_alias(ctx.obj["config_path"], alias)
    client = ReductClient(alias["url"], api_token=alias["token"])

    try:
        buckets: List[BucketInfo] = run(client.list())
        if full:
            table = Table()
            table.add_column("Name", justify="right", style="green")
            table.add_column("Entry Count")
            table.add_column("Size")
            table.add_column("Oldest Record")
            table.add_column("Latest Record")

            total_size = 0
            total_entry_count = 0
            oldest_record = None
            latest_record = None

            def print_datetime(time_stamp: int, valid: bool):
                return (
                    datetime.fromtimestamp(time_stamp / 1000_000).isoformat()
                    if valid
                    else "---"
                )

            for bckt in buckets:
                total_size += bckt.size
                total_entry_count += bckt.entry_count
                has_data = bckt.size > 0

                if has_data:
                    oldest_record = (
                        min(oldest_record, bckt.oldest_record)
                        if oldest_record
                        else bckt.oldest_record
                    )
                    latest_record = (
                        max(latest_record, bckt.latest_record)
                        if latest_record
                        else bckt.latest_record
                    )

                table.add_row(
                    bckt.name,
                    str(bckt.entry_count),
                    data_size(bckt.size),
                    print_datetime(bckt.oldest_record, has_data),
                    print_datetime(bckt.latest_record, has_data),
                )

            table.add_section()
            table.add_row(
                f"Total for {len(buckets)} buckets",
                str(total_entry_count),
                data_size(total_size),
                print_datetime(oldest_record, oldest_record),
                print_datetime(latest_record, oldest_record),
            )

            console.print(table)
        else:
            for bckt in buckets:
                console.print(bckt.name)

    except RuntimeError as err:
        console.print("Status: [red]Error[/red]")
        error_console.print(err)
