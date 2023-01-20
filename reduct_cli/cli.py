"""Main module"""
from importlib import metadata
from pathlib import Path
from typing import Optional

import click

from reduct_cli.config import write_config
from reduct_cli.alias import alias
from reduct_cli.bucket import bucket
from reduct_cli.server import server
from reduct_cli.mirror import mirror
from reduct_cli.token import token
from reduct_cli.export import export


@click.group()
@click.version_option(metadata.version("reduct-cli"))
@click.option(
    "--config",
    "-c",
    type=Path,
    help="Path to config file. Default ${HOME}/.reduct-cli/config.toml",
)
@click.option(
    "--timeout",
    "-t",
    type=int,
    help="Timeout for requests in seconds. Default 5",
)
@click.option(
    "--parallel",
    "-p",
    type=int,
    help="Number of parallel tasks to use, defaults to 10",
)
@click.pass_context
def cli(
    ctx,
    config: Optional[Path] = None,
    timeout: Optional[int] = None,
    parallel: Optional[int] = None,
):
    """CLI admin tool for Reduct Storage"""
    if config is None:
        config = Path.home() / ".reduct-cli" / "config.toml"

    if timeout is None:
        timeout = 5

    if parallel is None:
        parallel = 10

    if not Path.exists(config):
        write_config(config, {"aliases": {}})

    ctx.obj["config_path"] = config
    ctx.obj["timeout"] = timeout
    ctx.obj["parallel"] = parallel


cli.add_command(alias, "alias")
cli.add_command(bucket, "bucket")
cli.add_command(server, "server")
cli.add_command(mirror, "mirror")
cli.add_command(token, "token")
cli.add_command(export, "export")
