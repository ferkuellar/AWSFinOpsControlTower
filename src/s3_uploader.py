from datetime import datetime
from pathlib import Path

from rich.console import Console

from aws_clients import client

console = Console()


def upload_reports_to_s3(
    profile: str,
    region: str,
    bucket_name: str,
    local_reports_dir: str = "reports",
    prefix: str = "reports",
):
    s3 = client("s3", profile, region)

    reports_dir = Path(local_reports_dir)

    if not reports_dir.exists():
        console.print(f"[yellow]Reports directory does not exist:[/yellow] {reports_dir}")
        return []

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    uploaded = []

    for file_path in reports_dir.glob("*"):
        if not file_path.is_file():
            continue

        key = f"{prefix}/{timestamp}/{file_path.name}"

        try:
            s3.upload_file(
                Filename=str(file_path),
                Bucket=bucket_name,
                Key=key,
            )

            s3_uri = f"s3://{bucket_name}/{key}"
            uploaded.append(s3_uri)

            console.print(f"[green]Uploaded:[/green] {s3_uri}")

        except Exception as error:
            console.print(f"[red]Failed to upload {file_path}:[/red] {error}")

    return uploaded