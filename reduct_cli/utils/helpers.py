"""Helper functions"""
from pathlib import Path
from typing import Tuple

from click import Abort

from reduct_cli.config import read_config, Alias
from reduct_cli.utils.consoles import error_console


def get_alias(config_path: Path, name: str) -> Alias:
    """Helper method to parse alias from config"""
    conf = read_config(config_path)

    if name not in conf["aliases"]:
        error_console.print(f"Alias '{name}' doesn't exist")
        raise Abort()
    alias_: Alias = conf["aliases"][name]
    return alias_


def parse_path(path) -> Tuple[str, str]:
    """Parse path ALIAS/RESOURCE"""
    args = path.split("/")
    if len(args) != 2:
        raise RuntimeError(
            f"Path {path} has wrong format. It must be 'ALIAS/BUCKET_NAME'"
        )
    return tuple(args)
