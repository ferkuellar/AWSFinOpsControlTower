from rich.console import Console
from rich.panel import Panel
from rich.align import Align

console = Console()


def print_banner(title: str):
    console.print(
        Panel(
            Align.center(
                f"[bold white]{title}[/bold white]\n"
                "[cyan]Inventory • Cost • Risk • Recommendations • Reports[/cyan]"
            ),
            border_style="cyan",
            padding=(1, 4),
        )
    )