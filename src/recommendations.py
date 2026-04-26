from rich.console import Console
from rich.table import Table

console = Console()


def get_ec2_recommendation(instance: dict):
    avg_cpu = instance.get("avg_cpu_7d")

    missing_tags = (
        instance.get("owner") == "NO_TAG"
        or instance.get("environment") == "NO_TAG"
    )

    risk = "LOW"
    recommendation = "KEEP"

    if instance.get("state") == "stopped":
        risk = "MEDIUM"
        recommendation = "REVIEW STOPPED INSTANCE"

    elif avg_cpu is not None:
        if avg_cpu < 5:
            risk = "HIGH"
            recommendation = "TERMINATE / STOP CANDIDATE"
        elif avg_cpu < 20:
            risk = "MEDIUM"
            recommendation = "RIGHTSIZE CANDIDATE"
        else:
            risk = "LOW"
            recommendation = "KEEP"

    if missing_tags:
        risk = "HIGH"
        recommendation = f"{recommendation} + FIX TAGGING"

    return risk, recommendation


def get_ebs_recommendation(volume: dict):
    if volume.get("attached_to") == "UNATTACHED":
        return "DELETE CANDIDATE"

    if volume.get("type") == "gp2":
        return "MIGRATE GP2 TO GP3"

    return "KEEP"


def analyze_ec2(instances: list):
    table = Table(title="EC2 FinOps Recommendations")
    table.add_column("Region", style="magenta")
    table.add_column("Instance ID", style="cyan")
    table.add_column("State")
    table.add_column("Avg CPU 7d", justify="right")
    table.add_column("Risk")
    table.add_column("Recommendation", style="bold")

    for instance in instances:
        risk, recommendation = get_ec2_recommendation(instance)

        instance["risk"] = risk
        instance["recommendation"] = recommendation

        risk_display = {
            "LOW": "[green]LOW[/green]",
            "MEDIUM": "[yellow]MEDIUM[/yellow]",
            "HIGH": "[red]HIGH[/red]",
        }.get(risk, risk)

        if "TERMINATE" in recommendation:
            recommendation_display = f"[red]{recommendation}[/red]"
        elif "RIGHTSIZE" in recommendation or "REVIEW" in recommendation:
            recommendation_display = f"[yellow]{recommendation}[/yellow]"
        elif "FIX TAGGING" in recommendation:
            recommendation_display = f"[yellow]{recommendation}[/yellow]"
        else:
            recommendation_display = f"[green]{recommendation}[/green]"

        cpu_display = (
            "N/A"
            if instance.get("avg_cpu_7d") is None
            else f"{instance.get('avg_cpu_7d')}%"
        )

        table.add_row(
            instance.get("region", "N/A"),
            instance.get("id", "N/A"),
            instance.get("state", "N/A"),
            cpu_display,
            risk_display,
            recommendation_display,
        )

    console.print(table)

    return instances


def analyze_ebs(volumes: list):
    table = Table(title="EBS FinOps Recommendations")
    table.add_column("Region", style="magenta")
    table.add_column("Volume ID", style="cyan")
    table.add_column("Type")
    table.add_column("Size GiB", justify="right")
    table.add_column("Attached To")
    table.add_column("Recommendation", style="bold")

    for volume in volumes:
        recommendation = get_ebs_recommendation(volume)
        volume["recommendation"] = recommendation

        if "DELETE" in recommendation:
            recommendation_display = f"[red]{recommendation}[/red]"
        elif "MIGRATE" in recommendation:
            recommendation_display = f"[yellow]{recommendation}[/yellow]"
        else:
            recommendation_display = f"[green]{recommendation}[/green]"

        table.add_row(
            volume.get("region", "N/A"),
            volume.get("id", "N/A"),
            volume.get("type", "N/A"),
            str(volume.get("size", "N/A")),
            volume.get("attached_to", "N/A"),
            recommendation_display,
        )

    console.print(table)

    return volumes