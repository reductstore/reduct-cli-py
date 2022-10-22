"""Rich consoles"""
from rich.console import Console

error_console = Console(stderr=True, style="bold red")
console = Console()
