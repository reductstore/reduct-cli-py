"""Reduct CLI"""

from reduct_cli.cli import cli


def main():
    """Entry point to call from scripts"""
    return cli(obj={})  # pylint:disable=unexpected-keyword-arg, no-value-for-parameter
