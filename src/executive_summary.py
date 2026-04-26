from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.columns import Columns

console = Console()


def count_by_recommendation(items, keyword):
    return sum(
        1 for item in items
        if keyword.upper() in str(item.get("recommendation", "")).upper()
    )


def print_executive_summary(report: dict):
    ec2 = report.get("ec2_instances", [])
    ebs = report.get("ebs_volumes", [])
    rds = report.get("rds_instances", [])
    eips = report.get("elastic_ips", [])
    nat = report.get("nat_gateways", [])
    lbs = report.get("load_balancers", [])
    lambdas = report.get("lambda_functions", [])
    s3 = report.get("s3_buckets", [])

    total_resources = (
        len(ec2)
        + len(ebs)
        + len(rds)
        + len(eips)
        + len(nat)
        + len(lbs)
        + len(lambdas)
        + len(s3)
    )

    terminate_candidates = count_by_recommendation(ec2, "TERMINATE")
    rightsizing_candidates = count_by_recommendation(ec2, "RIGHTSIZE")
    unattached_ebs = count_by_recommendation(ebs, "DELETE")
    gp3_migration = count_by_recommendation(ebs, "GP3")
    unused_eips = count_by_recommendation(eips, "RELEASE")
    lifecycle_missing = count_by_recommendation(s3, "LIFECYCLE")
    rds_review = count_by_recommendation(rds, "REVIEW")
    nat_review = count_by_recommendation(nat, "VERIFY")
    lambda_review = count_by_recommendation(lambdas, "REVIEW")

    high_impact = terminate_candidates + unattached_ebs + unused_eips

    optimization_findings = (
        rightsizing_candidates
        + gp3_migration
        + lifecycle_missing
        + rds_review
        + nat_review
        + lambda_review
    )

    cards = [
        Panel(
            f"[bold cyan]{total_resources}[/bold cyan]\nTotal Resources",
            title="Inventory",
            border_style="cyan",
        ),
        Panel(
            f"[bold red]{high_impact}[/bold red]\nHigh Impact Findings",
            title="Immediate Action",
            border_style="red",
        ),
        Panel(
            f"[bold yellow]{optimization_findings}[/bold yellow]\nOptimization Findings",
            title="Review",
            border_style="yellow",
        ),
    ]

    console.print(Columns(cards))

    table = Table(title="Executive FinOps Summary")
    table.add_column("Area", style="cyan")
    table.add_column("Finding", style="white")
    table.add_column("Count", justify="right", style="bold")
    table.add_column("Action", style="bold")

    table.add_row(
        "EC2",
        "Low CPU / terminate-stop candidates",
        str(terminate_candidates),
        "[red]Validate owner, then stop/terminate[/red]",
    )

    table.add_row(
        "EC2",
        "Rightsizing candidates",
        str(rightsizing_candidates),
        "[yellow]Resize after workload validation[/yellow]",
    )

    table.add_row(
        "EBS",
        "Unattached volumes",
        str(unattached_ebs),
        "[red]Snapshot if needed, then delete[/red]",
    )

    table.add_row(
        "EBS",
        "GP2 volumes",
        str(gp3_migration),
        "[yellow]Migrate GP2 to GP3[/yellow]",
    )

    table.add_row(
        "Elastic IP",
        "Unused public IPs",
        str(unused_eips),
        "[red]Release unused Elastic IPs[/red]",
    )

    table.add_row(
        "S3",
        "Buckets without lifecycle policy",
        str(lifecycle_missing),
        "[yellow]Add lifecycle policy[/yellow]",
    )

    table.add_row(
        "RDS",
        "Databases requiring review",
        str(rds_review),
        "[yellow]Review Multi-AZ, storage, dev usage[/yellow]",
    )

    table.add_row(
        "NAT Gateway",
        "NAT Gateways requiring traffic validation",
        str(nat_review),
        "[yellow]Validate traffic and architecture[/yellow]",
    )

    table.add_row(
        "Lambda",
        "Functions requiring memory/timeout review",
        str(lambda_review),
        "[yellow]Tune memory and timeout[/yellow]",
    )

    console.print(table)