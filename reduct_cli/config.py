import os
from pathlib import Path
from typing import TypedDict, Dict

import tomlkit as toml


class Alias(TypedDict):
    url: str
    token: str


class Config(TypedDict):
    aliases: Dict[str, Alias]


def write_config(path: Path, config: Config):
    if not Path.exists(path):
        os.makedirs(path.parent, exist_ok=True)
    with open(path, "w") as config_file:
        config_file.write(toml.dumps(config))


def read_config(path: Path) -> Config:
    with open(path, "r") as config_file:
        return toml.loads(config_file.read())
