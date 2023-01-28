"""Depricated mirror command"""
from typing import Optional

import click

from reduct_cli.export import stop_option, start_option, entries_option, bucket
from reduct_cli.utils.consoles import error_console


@click.command()
@click.argument("src")
@click.argument("dest")
@stop_option
@start_option
@entries_option
@click.pass_context
def mirror(
    ctx, src: str, dest: str, start: Optional[str], stop: Optional[str], entries: str
):  # pylint: disable=too-many-arguments, unused-argument
    """Copy data from ALIAS_SRC/BUCKET to ALIAS_DST/BUCKET
    DEPRECATED: Use export bucket instead
    """
    error_console.print(
        "Command [b]mirror[/b] is deprecated. Use [b]export bucket[/b] instead"
    )
    ctx.forward(bucket)
