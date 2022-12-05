"""Error handling"""
from contextlib import contextmanager

from click import Abort

from reduct_cli.utils.consoles import error_console


@contextmanager
def error_handle():
    """Wrap try-catch block and print errorr"""
    try:
        yield
    except Exception as err:
        error_console.print(f"[{type(err).__name__}] {err}")
        raise Abort() from err
