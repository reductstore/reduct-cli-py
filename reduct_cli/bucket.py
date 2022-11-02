"""Bucket commands"""
from asyncio import new_event_loop as loop
from typing import List, Optional, Tuple

import click
from reduct import Client as ReductClient, BucketInfo, Bucket, BucketSettings, QuotaType
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table

from reduct_cli.alias import get_alias
from reduct_cli.consoles import console
from reduct_cli.error import error_handle
from reduct_cli.humanize import pretty_size, print_datetime, parse_ci_size
from reduct_cli.humanize import pretty_time_interval

run = loop().run_until_complete


def __parse_path(path) -> Tuple[str, str]:
    args = path.split("/")
    if len(args) != 2:
        raise RuntimeError(
            f"Path {path} has wrong format. It must be 'ALIAS/BUCKET_NAME'"
        )
    return tuple(args)


def __get_bucket_by_path(ctx, path):
    alias_name, bucket_name = __parse_path(path)
    alias = get_alias(ctx.obj["config_path"], alias_name)
    client = ReductClient(
        alias["url"], api_token=alias["token"], timeout=ctx.obj["timeout"]
    )
    bucket: Bucket = run(client.get_bucket(bucket_name))
    return bucket


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

    with error_handle():
        bucket = __get_bucket_by_path(ctx, path)

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
            # TODO: Fix when https://github.com/reduct-storage/reduct-py/issues/48 is done

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


@bucket_cmd.command()
@click.argument("path")
@click.option("--quota-type", "-Q", help="Quota type. Must be NONE or FIFO")
@click.option("--quota-size", "-s", help="Quota size in CI format e.g. 1Mb or 3TB")
@click.option("--block-size", "-b", help="Max. bock size in CI format e.g 64MB")
@click.option("--block-records", "-R", help="Max. number of records in a block")
@click.pass_context
def create(
    ctx,
    path: str,
    quota_type: Optional[QuotaType],
    quota_size: Optional[str],
    block_size: Optional[str],
    block_records: Optional[int],
):  # pylint: disable=too-many-arguments
    """Create a new bucket

    PATH should contain alias name and bucket name - ALIAS/BUCKET_NAME
    """
    with error_handle():
        alias_name, bucket_name = __parse_path(path)
        alias = get_alias(ctx.obj["config_path"], alias_name)
        client = ReductClient(
            alias["url"], api_token=alias["token"], timeout=ctx.obj["timeout"]
        )

        settings = BucketSettings(
            quota_type=quota_type,
            quota_size=parse_ci_size(quota_size),
            max_block_size=parse_ci_size(block_size),
            max_block_records=block_records,
        )
        run(client.create_bucket(bucket_name, settings))
        console.print(f"Bucket '{bucket_name}' created")


@bucket_cmd.command()
@click.argument("path")
@click.option("--quota-type", "-Q", help="Quota type. Must be NONE or FIFO")
@click.option("--quota-size", "-s", help="Quota size in CI format e.g. 1Mb or 3TB")
@click.option("--block-size", "-b", help="Max. bock size in CI format e.g 64MB")
@click.option("--block-records", "-R", help="Max. number of records in a block")
@click.pass_context
def update(
    ctx,
    path: str,
    quota_type: Optional[QuotaType],
    quota_size: Optional[str],
    block_size: Optional[str],
    block_records: Optional[int],
):  # pylint: disable=too-many-arguments
    """Update a bucket

    PATH should contain alias name and bucket name - ALIAS/BUCKET_NAME
    """
    with error_handle():
        bucket = __get_bucket_by_path(ctx, path)

        settings = BucketSettings(
            quota_type=quota_type,
            quota_size=parse_ci_size(quota_size),
            max_block_size=parse_ci_size(block_size),
            max_block_records=block_records,
        )
        run(bucket.set_settings(settings))
        console.print(f"Bucket '{bucket.name}' was updated")


@bucket_cmd.command()
@click.argument("path")
@click.pass_context
def rm(ctx, path: str):
    """
    Remove bucket

    PATH should contain alias name and bucket name - ALIAS/BUCKET_NAME
    """
    with error_handle():
        bucket = __get_bucket_by_path(ctx, path)
        console.print(
            f"All data in bucket [b]'{bucket.name}'[/b] will be [b]REMOVED[/b]."
        )
        if click.confirm("Do you want to continue?"):
            run(bucket.remove())
            console.print(f"Bucket '{bucket.name}' was removed")
        else:
            console.print("Canceled")
