"""Export Command"""
from asyncio import new_event_loop as loop
from typing import Optional

import click
from reduct import Client as ReductClient

from reduct_cli.export_impl.bucket import export_to_bucket
from reduct_cli.export_impl.folder import export_to_folder
from reduct_cli.utils.error import error_handle
from reduct_cli.utils.helpers import (
    parse_path,
    get_alias,
)

run = loop().run_until_complete

start_option = click.option(
    "--start",
    help="Export records with timestamps newer than this time point in ISO format",
)

stop_option = click.option(
    "--stop",
    help="Export records  with timestamps older than this time point in ISO format",
)
entries_option = click.option(
    "--entries",
    help="Export only these entries, separated by comma",
    default="",
)

include_option = click.option(
    "--include",
    help="Export only these records which have these labels with given values, "
    "separated by comma. Example: --include label1=values1,label2=value2",
    default="",
)

exclude_option = click.option(
    "--exclude",
    help="Export only these records which DON NOT have these labels with given values, "
    "separated by comma. Example: --exclude label1=values1,label2=value2",
    default="",
)


@click.group()
def export():
    """Export data from a bucket somewhere else"""


@export.command()
@click.argument("src")
@click.argument("dest")
@stop_option
@start_option
@entries_option
@include_option
@exclude_option
@click.option(
    "--ext",
    help="Extension for exported files, if not specified, will be guessed from content type",
)
@click.pass_context
def folder(
    ctx,
    src: str,
    dest: str,
    start: Optional[str],
    stop: Optional[str],
    entries: str,
    include: str,
    exclude: str,
    ext: Optional[str],
):  # pylint: disable=too-many-arguments
    """Export data from SRC bucket to DST folder

    SRC should be in the format of ALIAS/BUCKET_NAME.
    DST should be a path to a folder.

    As result, the folder will contain a folder for each entry in the bucket.
    Each entry folder will contain a file for each record
    in the entry with the timestamp as the name.
    """

    with error_handle():
        alias_name, src_bucket = parse_path(src)
        alias = get_alias(ctx.obj["config_path"], alias_name)

        client = ReductClient(
            alias["url"], api_token=alias["token"], timeout=ctx.obj["timeout"]
        )
        run(
            export_to_folder(
                client,
                dest,
                src_bucket,
                parallel=ctx.obj["parallel"],
                start=start,
                stop=stop,
                entries=entries.split(","),
                include=include.split(","),
                exclude=exclude.split(","),
                ext=ext,
            )
        )


@export.command
@click.argument("src")
@click.argument("dest")
@stop_option
@start_option
@entries_option
@include_option
@exclude_option
@click.pass_context
def bucket(
    ctx,
    src: str,
    dest: str,
    start: Optional[str],
    stop: Optional[str],
    entries: str,
    include: str,
    exclude: str,
):  # pylint: disable=too-many-arguments
    """Copy data from SRC to DEST bucket

    SRC and DST should be in the format of ALIAS/BUCKET_NAME

    If the destination bucket doesn't exist, it is created with
    the settings of the source bucket."""

    with error_handle():
        alias_name, src_bucket = parse_path(src)
        alias = get_alias(ctx.obj["config_path"], alias_name)
        src_instance = ReductClient(
            alias["url"], api_token=alias["token"], timeout=ctx.obj["timeout"]
        )

        alias_name, dest_bucket = parse_path(dest)
        alias = get_alias(ctx.obj["config_path"], alias_name)
        dest_instance = ReductClient(
            alias["url"], api_token=alias["token"], timeout=ctx.obj["timeout"]
        )

        run(
            export_to_bucket(
                src_bucket,
                dest_bucket,
                src_instance,
                dest_instance,
                parallel=ctx.obj["parallel"],
                start=start,
                stop=stop,
                entries=entries.split(","),
                include=include.split(","),
                exclude=exclude.split(","),
            )
        )
