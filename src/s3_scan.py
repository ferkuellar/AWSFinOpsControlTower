from rich.console import Console
from rich.table import Table

from aws_clients import global_client

console = Console()


def scan_s3_buckets(profile: str):
    s3 = global_client("s3", profile)
    buckets = []

    try:
        response = s3.list_buckets()
    except Exception as error:
        console.print(f"[yellow]S3 scan skipped: {error}[/yellow]")
        return buckets

    table = Table(title="S3 Buckets")
    table.add_column("Bucket", style="cyan")
    table.add_column("Lifecycle")
    table.add_column("Recommendation", style="bold")

    for bucket in response.get("Buckets", []):
        name = bucket.get("Name")
        has_lifecycle = True

        try:
            s3.get_bucket_lifecycle_configuration(Bucket=name)
        except Exception:
            has_lifecycle = False

        recommendation = "KEEP" if has_lifecycle else "ADD LIFECYCLE POLICY"

        item = {
            "bucket": name,
            "has_lifecycle": has_lifecycle,
            "recommendation": recommendation,
        }

        buckets.append(item)

        table.add_row(
            name,
            str(has_lifecycle),
            recommendation,
        )

    console.print(table)
    return buckets