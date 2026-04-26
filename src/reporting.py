import csv
import json
from datetime import datetime
from pathlib import Path

REPORT_DIR = Path("reports")


def ensure_reports_dir():
    REPORT_DIR.mkdir(exist_ok=True)


def timestamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def export_json(data: dict, filename_prefix: str = "finops_report"):
    ensure_reports_dir()

    file_path = REPORT_DIR / f"{filename_prefix}_{timestamp()}.json"

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, default=str)

    return file_path


def export_csv_ec2(instances: list, filename_prefix: str = "ec2_inventory"):
    ensure_reports_dir()

    file_path = REPORT_DIR / f"{filename_prefix}_{timestamp()}.csv"

    fieldnames = [
        "region",
        "id",
        "name",
        "type",
        "state",
        "avg_cpu_7d",
        "owner",
        "environment",
        "risk",
        "recommendation",
    ]

    with open(file_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for instance in instances:
            writer.writerow({
                "region": instance.get("region"),
                "id": instance.get("id"),
                "name": instance.get("name"),
                "type": instance.get("type"),
                "state": instance.get("state"),
                "avg_cpu_7d": instance.get("avg_cpu_7d"),
                "owner": instance.get("owner"),
                "environment": instance.get("environment"),
                "risk": instance.get("risk"),
                "recommendation": instance.get("recommendation"),
            })

    return file_path


def export_csv_ebs(volumes: list, filename_prefix: str = "ebs_inventory"):
    ensure_reports_dir()

    file_path = REPORT_DIR / f"{filename_prefix}_{timestamp()}.csv"

    fieldnames = [
        "region",
        "id",
        "type",
        "size",
        "state",
        "attached_to",
        "recommendation",
    ]

    with open(file_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for volume in volumes:
            writer.writerow({
                "region": volume.get("region"),
                "id": volume.get("id"),
                "type": volume.get("type"),
                "size": volume.get("size"),
                "state": volume.get("state"),
                "attached_to": volume.get("attached_to"),
                "recommendation": volume.get("recommendation"),
            })

    return file_path