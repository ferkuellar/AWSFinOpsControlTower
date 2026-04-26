import typer
from rich.console import Console
from rich.progress import track

from ui import print_banner
from regions import get_enabled_regions
from inventory import scan_ec2_instances, scan_ebs_volumes

app = typer.Typer()
console = Console()


@app.command()
def scan(
    profile: str = "finops-lab",
    region: str = "us-east-1",
    all_regions: bool = False,
):
    print_banner("AWS FINOPS CONTROL TOWER")

    regions = get_enabled_regions(profile) if all_regions else [region]

    all_instances = []
    all_volumes = []

    for current_region in track(regions, description="Scanning AWS regions..."):
        console.rule(f"[bold cyan]Region: {current_region}")

        instances = scan_ec2_instances(profile, current_region)
        volumes = scan_ebs_volumes(profile, current_region)

        all_instances.extend(instances)
        all_volumes.extend(volumes)

    console.rule("[bold green]Scan Summary")
    console.print(f"[green]EC2 instances found:[/green] {len(all_instances)}")
    console.print(f"[green]EBS volumes found:[/green] {len(all_volumes)}")


if __name__ == "__main__":
    app()