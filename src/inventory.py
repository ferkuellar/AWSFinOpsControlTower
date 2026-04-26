from rich.console import Console
from rich.table import Table

from aws_clients import client
from metrics import get_ec2_avg_cpu

console = Console()


def get_tag(tags, key):
    if not tags:
        return "NO_TAG"

    for tag in tags:
        if tag.get("Key") == key:
            return tag.get("Value")

    return "NO_TAG"


def scan_ec2_instances(profile: str, region: str):
    ec2 = client("ec2", profile, region)

    response = ec2.describe_instances()

    instances = []

    table = Table(title=f"EC2 Instances | {region}")
    table.add_column("Region", style="magenta")
    table.add_column("Instance ID", style="cyan")
    table.add_column("Name")
    table.add_column("Type", style="yellow")
    table.add_column("State")
    table.add_column("Avg CPU 7d", justify="right")
    table.add_column("Owner")
    table.add_column("Environment")

    for reservation in response.get("Reservations", []):
        for instance in reservation.get("Instances", []):
            instance_id = instance["InstanceId"]
            state = instance["State"]["Name"]

            avg_cpu = None

            if state == "running":
                avg_cpu = get_ec2_avg_cpu(
                    profile=profile,
                    region=region,
                    instance_id=instance_id
                )

            item = {
                "region": region,
                "id": instance_id,
                "name": get_tag(instance.get("Tags", []), "Name"),
                "type": instance["InstanceType"],
                "state": state,
                "avg_cpu_7d": avg_cpu,
                "owner": get_tag(instance.get("Tags", []), "Owner"),
                "environment": get_tag(instance.get("Tags", []), "Environment"),
            }

            instances.append(item)

            cpu_display = "N/A" if avg_cpu is None else f"{avg_cpu}%"

            table.add_row(
                item["region"],
                item["id"],
                item["name"],
                item["type"],
                item["state"],
                cpu_display,
                item["owner"],
                item["environment"],
            )

    console.print(table)

    return instances


def scan_ebs_volumes(profile: str, region: str):
    ec2 = client("ec2", profile, region)

    response = ec2.describe_volumes()

    volumes = []

    table = Table(title=f"EBS Volumes | {region}")
    table.add_column("Region", style="magenta")
    table.add_column("Volume ID", style="cyan")
    table.add_column("Type", style="yellow")
    table.add_column("Size GiB", justify="right")
    table.add_column("State")
    table.add_column("Attached To")

    for volume in response.get("Volumes", []):
        attached_to = "UNATTACHED"

        if volume.get("Attachments"):
            attached_to = volume["Attachments"][0].get(
                "InstanceId",
                "UNKNOWN"
            )

        item = {
            "region": region,
            "id": volume["VolumeId"],
            "type": volume["VolumeType"],
            "size": volume["Size"],
            "state": volume["State"],
            "attached_to": attached_to,
        }

        volumes.append(item)

        table.add_row(
            item["region"],
            item["id"],
            item["type"],
            str(item["size"]),
            item["state"],
            item["attached_to"],
        )

    console.print(table)

    return volumes