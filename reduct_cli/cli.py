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


@click.group()
@click.version_option(metadata.version("reduct-cli"))
@click.option(
    "--config",
    "-c",
    type=Path,
    help="Path to config file. Default ${HOME}/.reduct-cli/config.toml",
)
@click.pass_context
def cli(ctx, config: Optional[Path] = None):
    """CLI admin tool for Reduct Storage"""
    if config is None:
        config = Path.home() / ".reduct-cli" / "config.toml"

    if not Path.exists(config):
        write_config(config, {"aliases": {}})

    ctx.obj["config_path"] = config
    ctx.obj["timeout"] = 3.0


cli.add_command(alias, "alias")
cli.add_command(bucket, "bucket")
cli.add_command(server, "server")
cli.add_command(mirror, "mirror")
cli.add_command(token, "token")
