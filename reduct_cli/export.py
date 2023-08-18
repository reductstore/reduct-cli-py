"""Export Command"""
from asyncio import new_event_loop as loop
from typing import Optional

import click

from reduct_cli.export_impl.bucket import export_to_bucket
from reduct_cli.export_impl.folder import export_to_folder
from reduct_cli.utils.error import error_handle
from reduct_cli.utils.helpers import (
    parse_path,
    build_client,
)

run = loop().run_until_complete

start_option = click.option(
    "--start",
    help="Export records with timestamps newer than this time point in ISO format"
    " or Unix timestamp in microseconds",
)

stop_option = click.option(
    "--stop",
    help="Export records  with timestamps older than this time point in ISO format"
    " or Unix timestamp in microseconds",
)

entries_option = click.option(
    "--entries",
    "-e",
    help="Export only these entries, separated by comma",
    default="",
)

include_option = click.option(
    "--include",
    "-I",
    help="Export only these records which have these labels with given values, "
    "separated by comma. Example: --include label1=values1,label2=value2",
    default="",
)

exclude_option = click.option(
    "--exclude",
    "-E",
    help="Export only these records which DON NOT have these labels with given values, "
    "separated by comma. Example: --exclude label1=values1,label2=value2",
    default="",
)

limit_option = click.option(
    "--limit", "-l", help="Limit the number of records to export"
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
@limit_option
@click.option(
    "--ext",
    help="Extension for exported files, if not specified, will be guessed from content type",
)
@click.option(
    "--with-metadata/--no-with-metadata",
    help="Export metadata along with the data",
    default=False,
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
    with_metadata: bool,
    limit: Optional[int],
):  # pylint: disable=too-many-arguments
    """Export data from SRC bucket to DST folder

    SRC should be in the format of ALIAS/BUCKET_NAME.
    DST should be a path to a folder.

    As result, the folder will contain a folder for each entry in the bucket.
    Each entry folder will contain a file for each record
    in the entry with the timestamp as the name.
    """

    alias_name, src_bucket = parse_path(src)
    client = build_client(
        ctx.obj["config_path"], alias_name, timeout=ctx.obj["timeout"]
    )
    with error_handle():
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
                timeout=ctx.obj["timeout"],
                with_metadata=with_metadata,
                limit=limit,
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
@limit_option
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
    limit: Optional[int],
):  # pylint: disable=too-many-arguments
    """Copy data from SRC to DEST bucket

    SRC and DST should be in the format of ALIAS/BUCKET_NAME

    If the destination bucket doesn't exist, it is created with
    the settings of the source bucket."""

    with error_handle():
        alias_name, src_bucket = parse_path(src)
        src_instance = build_client(
            ctx.obj["config_path"], alias_name, timeout=ctx.obj["timeout"]
        )

        alias_name, dest_bucket = parse_path(dest)
        dest_instance = build_client(
            ctx.obj["config_path"], alias_name, timeout=ctx.obj["timeout"]
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
                timeout=ctx.obj["timeout"],
                limit=limit,
            )
        )
