import typer
from rich.console import Console

from ui import print_banner
from regions import get_enabled_regions

app = typer.Typer()
console = Console()


@app.command()
def scan(
    profile: str = "default",
    region: str = "us-east-1",
    all_regions: bool = False,
):
    print_banner("AWS FINOPS CONTROL TOWER")

    regions = get_enabled_regions(profile) if all_regions else [region]

    console.rule("[bold cyan]Regions Selected")

    for selected_region in regions:
        console.print(f"[green]Region:[/green] {selected_region}")


if __name__ == "__main__":
    app()