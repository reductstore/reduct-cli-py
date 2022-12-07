"""Token command"""
from asyncio import new_event_loop as loop
from typing import List

import click
from reduct import Client as ReductClient, Permissions
from reduct import Token, FullTokenInfo

from reduct_cli.utils.consoles import console
from reduct_cli.utils.error import error_handle
from reduct_cli.utils.helpers import get_alias

run = loop().run_until_complete


@click.group()
def token():
    """Commands to manage API tokens"""


@token.command()
@click.argument("alias")
@click.pass_context
def ls(ctx, alias: str):
    """Print list of tokens"""
    alias_ = get_alias(ctx.obj["config_path"], alias)

    client = ReductClient(
        alias_["url"], api_token=alias_["token"], timeout=ctx.obj["timeout"]
    )

    with error_handle():
        tokens: List[Token] = run(client.get_token_list())
        for tkn in tokens:
            console.print(tkn.name)


@token.command()
@click.argument("alias")
@click.argument("name")
@click.pass_context
def show(ctx, alias: str, name: str):
    """Show token"""
    alias_ = get_alias(ctx.obj["config_path"], alias)
    client = ReductClient(
        alias_["url"], api_token=alias_["token"], timeout=ctx.obj["timeout"]
    )
    with error_handle():
        tkn: FullTokenInfo = run(client.get_token(name))
        console.print(f"Name:    {tkn.name}")
        console.print(f"Created At:     {tkn.created_at}")
        console.print(f"Full Access:    {tkn.permissions.full_access}")
        console.print(f"Read Only:      {tkn.permissions.read}")
        console.print(f"Write Only:     {tkn.permissions.write}")


@token.command()
@click.argument("alias")
@click.argument("name")
@click.option("--full-access", is_flag=True, help="Full access (admin)", default=False)
@click.option(
    "--read",
    help="Read access to list of buckets. Example: 'bucket-1,bucket-2'",
    default="",
)
@click.option(
    "--write",
    help="Write access to list of buckets. Example: 'bucket-1,bucket-2'",
    default="",
)
@click.pass_context
def create(
    ctx, alias: str, name: str, full_access: bool, read: str, write: str
):  # pylint: disable=too-many-arguments
    """Create token"""
    alias_ = get_alias(ctx.obj["config_path"], alias)

    client = ReductClient(
        alias_["url"], api_token=alias_["token"], timeout=ctx.obj["timeout"]
    )
    with error_handle():
        permissions = Permissions(
            full_access=full_access,
            read=read.replace(" ", "").split(","),
            write=write.replace(" ", "").split(","),
        )
        token_value = run(client.create_token(name, permissions))
        console.print(f"New token:    {token_value}")


@token.command()
@click.argument("alias")
@click.argument("name")
@click.pass_context
def rm(ctx, alias: str, name: str):
    """Remove token"""
    alias_ = get_alias(ctx.obj["config_path"], alias)

    client = ReductClient(
        alias_["url"], api_token=alias_["token"], timeout=ctx.obj["timeout"]
    )

    with error_handle():
        console.print(f"We are going to [b]remove[/b] token: {name}")
        if click.confirm("Do you want to continue?"):
            run(client.remove_token(name))
            console.print(f"Token '{name}' was deleted")
        else:
            console.print("Canceled")
