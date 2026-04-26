from rich.console import Console
from rich.table import Table

from aws_clients import client

console = Console()


def scan_rds_instances(profile: str, region: str):
    rds = client("rds", profile, region)
    instances = []

    try:
        response = rds.describe_db_instances()
    except Exception as error:
        console.print(f"[yellow]RDS scan skipped in {region}: {error}[/yellow]")
        return instances

    table = Table(title=f"RDS Instances | {region}")
    table.add_column("Region", style="magenta")
    table.add_column("DB ID", style="cyan")
    table.add_column("Class")
    table.add_column("Engine")
    table.add_column("Multi-AZ")
    table.add_column("Storage GB", justify="right")
    table.add_column("Status")
    table.add_column("Recommendation", style="bold")

    for db in response.get("DBInstances", []):
        db_id = db.get("DBInstanceIdentifier", "UNKNOWN")
        db_class = db.get("DBInstanceClass", "UNKNOWN")
        engine = db.get("Engine", "UNKNOWN")
        multi_az = db.get("MultiAZ", False)
        storage = db.get("AllocatedStorage", 0)
        status = db.get("DBInstanceStatus", "UNKNOWN")

        recommendation = "KEEP"

        if status == "stopped":
            recommendation = "REVIEW STOPPED RDS"
        elif multi_az and "dev" in db_id.lower():
            recommendation = "REVIEW MULTI-AZ IN DEV"
        elif storage > 500:
            recommendation = "REVIEW STORAGE SIZE"

        item = {
            "region": region,
            "id": db_id,
            "class": db_class,
            "engine": engine,
            "multi_az": multi_az,
            "storage": storage,
            "status": status,
            "recommendation": recommendation,
        }

        instances.append(item)

        table.add_row(
            region,
            db_id,
            db_class,
            engine,
            str(multi_az),
            str(storage),
            status,
            recommendation,
        )

    console.print(table)
    return instances