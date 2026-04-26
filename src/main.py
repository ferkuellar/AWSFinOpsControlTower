import typer
from rich.console import Console
from rich.progress import track

from ui import print_banner
from regions import get_enabled_regions
from costs import get_monthly_cost_by_service
from inventory import scan_ec2_instances, scan_ebs_volumes
from recommendations import analyze_ec2, analyze_ebs
from rds import scan_rds_instances
from s3_scan import scan_s3_buckets
from lambda_scan import scan_lambda_functions
from networking import (
    scan_elastic_ips,
    scan_nat_gateways,
    scan_load_balancers,
)
from reporting import (
    export_json,
    export_csv_ec2,
    export_csv_ebs,
)
from consolidated_report import generate_consolidated_markdown

app = typer.Typer()
console = Console()


@app.command()
def scan(
    profile: str = "default",
    region: str = "us-east-1",
    all_regions: bool = False,
    export: bool = True,
):
    print_banner("AWS FINOPS CONTROL TOWER")

    console.rule("[bold cyan]Cost Overview")
    cost_summary = get_monthly_cost_by_service(profile)

    regions = get_enabled_regions(profile) if all_regions else [region]

    all_instances = []
    all_volumes = []
    all_rds = []
    all_lambdas = []
    all_eips = []
    all_nat = []
    all_load_balancers = []

    console.rule("[bold cyan]Global Services")
    s3_buckets = scan_s3_buckets(profile)

    for current_region in track(regions, description="Scanning AWS regions..."):
        console.rule(f"[bold cyan]Region: {current_region}")

        all_instances.extend(scan_ec2_instances(profile, current_region))
        all_volumes.extend(scan_ebs_volumes(profile, current_region))
        all_rds.extend(scan_rds_instances(profile, current_region))
        all_lambdas.extend(scan_lambda_functions(profile, current_region))
        all_eips.extend(scan_elastic_ips(profile, current_region))
        all_nat.extend(scan_nat_gateways(profile, current_region))
        all_load_balancers.extend(scan_load_balancers(profile, current_region))

    console.rule("[bold cyan]Recommendations")

    analyzed_instances = analyze_ec2(all_instances)
    analyzed_volumes = analyze_ebs(all_volumes)

    report = {
        "profile": profile,
        "regions": regions,
        "cost_summary": cost_summary,
        "ec2_instances": analyzed_instances,
        "ebs_volumes": analyzed_volumes,
        "rds_instances": all_rds,
        "s3_buckets": s3_buckets,
        "lambda_functions": all_lambdas,
        "elastic_ips": all_eips,
        "nat_gateways": all_nat,
        "load_balancers": all_load_balancers,
    }

    console.rule("[bold green]Consolidated Report")
    consolidated_file = generate_consolidated_markdown(
        report=report,
        total_savings=0.0
    )

    console.print(
        f"[green]Executive Markdown Report:[/green] {consolidated_file}"
    )

    if export:
        json_file = export_json(report)
        ec2_csv = export_csv_ec2(analyzed_instances)
        ebs_csv = export_csv_ebs(analyzed_volumes)

        console.rule("[bold green]Reports Exported")
        console.print(f"[green]JSON:[/green] {json_file}")
        console.print(f"[green]EC2 CSV:[/green] {ec2_csv}")
        console.print(f"[green]EBS CSV:[/green] {ebs_csv}")

    console.rule("[bold green]Scan Summary")
    console.print(f"[green]Cost period:[/green] {cost_summary['start']} to {cost_summary['end']}")
    console.print(f"[green]Total monthly spend detected:[/green] ${cost_summary['total']:,.2f}")
    console.print(f"[green]EC2 instances found:[/green] {len(analyzed_instances)}")
    console.print(f"[green]EBS volumes found:[/green] {len(analyzed_volumes)}")
    console.print(f"[green]RDS instances found:[/green] {len(all_rds)}")
    console.print(f"[green]S3 buckets found:[/green] {len(s3_buckets)}")
    console.print(f"[green]Lambda functions found:[/green] {len(all_lambdas)}")
    console.print(f"[green]Elastic IPs found:[/green] {len(all_eips)}")
    console.print(f"[green]NAT Gateways found:[/green] {len(all_nat)}")
    console.print(f"[green]Load Balancers found:[/green] {len(all_load_balancers)}")


if __name__ == "__main__":
    app()