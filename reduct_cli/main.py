"""Main module"""

import click
from alias import alias

cli = click.CommandCollection(sources=[alias(obj={})])
