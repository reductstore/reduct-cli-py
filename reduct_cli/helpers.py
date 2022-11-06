"""Helper functions"""
from pathlib import Path
from typing import Tuple

from click import Abort
from reduct import Bucket, Client

from reduct_cli.consoles import error_console
from reduct_cli.config import read_config, Alias


def get_alias(config_path: Path, name: str) -> Alias:
    """Helper method to parse alias from config"""
    conf = read_config(config_path)

    if name not in conf["aliases"]:
        error_console.print(f"Alias '{name}' doesn't exist")
        raise Abort()
    alias_: Alias = conf["aliases"][name]
    return alias_


def parse_path(path) -> Tuple[str, str]:
    args = path.split("/")
    if len(args) != 2:
        raise RuntimeError(
            f"Path {path} has wrong format. It must be 'ALIAS/BUCKET_NAME'"
        )
    return tuple(args)


async def get_bucket_by_path(ctx, path):
    alias_name, bucket_name = parse_path(path)
    alias = get_alias(ctx.obj["config_path"], alias_name)
    client = Client(alias["url"], api_token=alias["token"], timeout=ctx.obj["timeout"])
    bucket: Bucket = await client.get_bucket(bucket_name)
    return bucket
