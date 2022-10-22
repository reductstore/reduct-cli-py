"""Configuration"""
import os
from pathlib import Path
from typing import TypedDict, Dict

import tomlkit as toml


class Alias(TypedDict):
    """Alias of storage instance"""

    url: str
    token: str


class Config(TypedDict):
    """Configuration as a dict"""

    aliases: Dict[str, Alias]


def write_config(path: Path, config: Config):
    """Write config to TOML file"""
    if not Path.exists(path):
        os.makedirs(path.parent, exist_ok=True)
    with open(path, "w", encoding="utf8") as config_file:
        config_file.write(toml.dumps(config))


def read_config(path: Path) -> Config:
    """Read config from TOML file"""
    with open(path, "r", encoding="utf8") as config_file:
        return toml.loads(config_file.read())
