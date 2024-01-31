"""Configuration"""
import os
from pathlib import Path
from typing import Dict, Annotated

import tomlkit as toml
from pydantic import HttpUrl, BaseModel
from pydantic.functional_validators import BeforeValidator
from pydantic.type_adapter import TypeAdapter

Url = Annotated[
    str, BeforeValidator(lambda value: str(TypeAdapter(HttpUrl).validate_python(value)))
]


class Alias(BaseModel):
    """Alias of storage instance"""

    url: Url
    token: str


class Config(BaseModel):
    """Configuration as a dict"""

    aliases: Dict[str, Alias] = {}


def write_config(path: Path, config: Config):
    """Write config to TOML file"""
    if not Path.exists(path):
        os.makedirs(path.parent, exist_ok=True)
    with open(path, "w", encoding="utf8") as config_file:
        toml.dump(config.model_dump(), config_file)


def read_config(path: Path) -> Config:
    """Read config from TOML file"""
    with open(path, "r", encoding="utf8") as config_file:
        return Config.model_validate(toml.load(config_file))
