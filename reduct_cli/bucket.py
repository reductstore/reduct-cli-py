"""Bucket commands"""
from asyncio import new_event_loop as loop
from typing import List

import click
from click import Abort
from reduct import Client as ReductClient, BucketInfo, Bucket, BucketSettings
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table

from reduct_cli.alias import get_alias
from reduct_cli.consoles import console, error_console
from reduct_cli.error import error_handle
from reduct_cli.humanize import pretty_size, print_datetime
from reduct_cli.humanize import pretty_time_interval

run = loop().run_until_complete


@click.group()
def bucket_cmd():
    """Commands to manage buckets"""


@bucket_cmd.command()
@click.argument("alias")
@click.option("--full/--no-full", help="Print full information", default=False)
@click.pass_context
def ls(ctx, alias: str, full: bool):
    """
    List buckets
    """
    alias = get_alias(ctx.obj["config_path"], alias)
    client = ReductClient(
        alias["url"], api_token=alias["token"], timeout=ctx.obj["timeout"]
    )

    with error_handle():
        buckets: List[BucketInfo] = run(client.list())
        if full:
            table = Table()
            table.add_column("Name", justify="right", style="green")
            table.add_column("Entry Count")
            table.add_column("Size")
            table.add_column("Oldest Record (UTC)")
            table.add_column("Latest Record (UTC)")

            total_size = 0
            total_entry_count = 0
            oldest_record = None
            latest_record = None

            for bucket in buckets:
                total_size += bucket.size
                total_entry_count += bucket.entry_count
                has_data = bucket.size > 0

                if has_data:
                    oldest_record = (
                        min(oldest_record, bucket.oldest_record)
                        if oldest_record
                        else bucket.oldest_record
                    )
                    latest_record = (
                        max(latest_record, bucket.latest_record)
                        if latest_record
                        else bucket.latest_record
                    )

                table.add_row(
                    bucket.name,
                    str(bucket.entry_count),
                    pretty_size(bucket.size),
                    print_datetime(bucket.oldest_record, has_data),
                    print_datetime(bucket.latest_record, has_data),
                )

            table.add_section()
            table.add_row(
                f"Total for {len(buckets)} buckets",
                str(total_entry_count),
                pretty_size(total_size),
                print_datetime(oldest_record, oldest_record),
                print_datetime(latest_record, oldest_record),
            )

            console.print(table)
        else:
            for bucket in buckets:
                console.print(bucket.name)


@bucket_cmd.command()
@click.argument("path")
@click.option("--full/--no-full", help="Print full information", default=False)
@click.pass_context
def show(ctx, path: str, full: bool):
    """
    Show information about bucket

    PATH should contain alias name and bucket name - ALIAS/BUCKET_NAME
    """
    args = path.split("/")
    if len(args) != 2:
        error_console.print(
            f"Path {path} has wrong format. It must be 'ALIAS/BUCKET_NAME'"
        )
        Abort()

    alias = get_alias(ctx.obj["config_path"], args[0])
    client = ReductClient(
        alias["url"], api_token=alias["token"], timeout=ctx.obj["timeout"]
    )

    with error_handle():
        bucket: Bucket = run(client.get_bucket(args[1]))
        # TODO: Fix when https://github.com/reduct-storage/reduct-py/issues/48 is done
        info: BucketInfo = run(bucket.info())
        history_interval = (info.latest_record - info.oldest_record) / 1000000

        info_txt = "\n".join(
            [
                f"Entry count:         {info.entry_count}",
                f"Size:                {pretty_size(info.size)}",
                f"Oldest Record (UTC): {print_datetime(info.oldest_record, info.size > 0)}",
                f"Latest Record (UTC): {print_datetime(info.latest_record, info.size > 0)}",
                f"History Interval:    {pretty_time_interval(history_interval)}",
            ]
        )

        if not full:
            console.print(info_txt)
        else:
            settings: BucketSettings = run(bucket.get_settings())
            settings_txt = "\n".join(
                [
                    f"Quota Type:         {settings.quota_type.name}",
                    f"Quota Size:         {pretty_size(settings.quota_size)}",
                    f"Max. Block Size:    {pretty_size(settings.max_block_size)}",
                    f"Max. Block Records: {settings.max_block_records}",
                ]
            )

            table = Table(title="Entries", expand=True)
            table.add_column("Name", justify="right", style="green")
            table.add_column("Records")
            table.add_column("Blocks")
            table.add_column("Size")
            table.add_column("Oldest Record (UTC)")
            table.add_column("Latest Record (UTC)")
            table.add_column("History")

            for entry in run(bucket.get_entry_list()):
                table.add_row(
                    entry.name,
                    str(entry.record_count),
                    str(entry.block_count),
                    pretty_size(entry.size),
                    print_datetime(entry.oldest_record, entry.size > 0),
                    print_datetime(entry.latest_record, entry.size > 0),
                    pretty_time_interval(
                        (entry.latest_record - entry.oldest_record) / 1000000
                    ),
                )

                layout = Layout()
                layout.split_column(Layout(name="upper"), Layout(table, visible=True))
                layout["upper"].split_row(
                    Layout(Panel(info_txt, title="Info"), minimum_size=50),
                    Layout(Panel(settings_txt, title="Settings")),
                )

                console.print(layout)
