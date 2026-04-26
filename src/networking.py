from rich.console import Console
from rich.table import Table

from aws_clients import client

console = Console()


def scan_elastic_ips(profile: str, region: str):
    ec2 = client("ec2", profile, region)
    elastic_ips = []

    try:
        response = ec2.describe_addresses()
    except Exception as error:
        console.print(f"[yellow]Elastic IP scan skipped in {region}: {error}[/yellow]")
        return elastic_ips

    table = Table(title=f"Elastic IPs | {region}")
    table.add_column("Region", style="magenta")
    table.add_column("Public IP", style="cyan")
    table.add_column("Allocation ID")
    table.add_column("Associated")
    table.add_column("Recommendation", style="bold")

    for ip in response.get("Addresses", []):
        associated = "AssociationId" in ip
        recommendation = "KEEP" if associated else "RELEASE UNUSED EIP"

        item = {
            "region": region,
            "public_ip": ip.get("PublicIp", "UNKNOWN"),
            "allocation_id": ip.get("AllocationId", "N/A"),
            "associated": associated,
            "recommendation": recommendation,
        }

        elastic_ips.append(item)

        table.add_row(
            region,
            item["public_ip"],
            item["allocation_id"],
            str(associated),
            recommendation,
        )

    console.print(table)
    return elastic_ips


def scan_nat_gateways(profile: str, region: str):
    ec2 = client("ec2", profile, region)
    nat_gateways = []

    try:
        response = ec2.describe_nat_gateways()
    except Exception as error:
        console.print(f"[yellow]NAT Gateway scan skipped in {region}: {error}[/yellow]")
        return nat_gateways

    table = Table(title=f"NAT Gateways | {region}")
    table.add_column("Region", style="magenta")
    table.add_column("NAT ID", style="cyan")
    table.add_column("State")
    table.add_column("VPC")
    table.add_column("Recommendation", style="bold")

    for nat in response.get("NatGateways", []):
        state = nat.get("State", "UNKNOWN")

        if state == "available":
            recommendation = "VERIFY TRAFFIC / HIGH COST RISK"
        else:
            recommendation = "REVIEW NAT STATE"

        item = {
            "region": region,
            "id": nat.get("NatGatewayId", "UNKNOWN"),
            "state": state,
            "vpc_id": nat.get("VpcId", "UNKNOWN"),
            "recommendation": recommendation,
        }

        nat_gateways.append(item)

        table.add_row(
            region,
            item["id"],
            item["state"],
            item["vpc_id"],
            recommendation,
        )

    console.print(table)
    return nat_gateways


def scan_load_balancers(profile: str, region: str):
    elbv2 = client("elbv2", profile, region)
    load_balancers = []

    try:
        response = elbv2.describe_load_balancers()
    except Exception as error:
        console.print(f"[yellow]Load Balancer scan skipped in {region}: {error}[/yellow]")
        return load_balancers

    table = Table(title=f"Load Balancers | {region}")
    table.add_column("Region", style="magenta")
    table.add_column("Name", style="cyan")
    table.add_column("Type")
    table.add_column("Scheme")
    table.add_column("State")
    table.add_column("Recommendation", style="bold")

    for lb in response.get("LoadBalancers", []):
        state = lb.get("State", {}).get("Code", "UNKNOWN")
        recommendation = "KEEP" if state == "active" else "REVIEW LB STATE"

        item = {
            "region": region,
            "name": lb.get("LoadBalancerName", "UNKNOWN"),
            "type": lb.get("Type", "UNKNOWN"),
            "scheme": lb.get("Scheme", "UNKNOWN"),
            "state": state,
            "recommendation": recommendation,
        }

        load_balancers.append(item)

        table.add_row(
            region,
            item["name"],
            item["type"],
            item["scheme"],
            item["state"],
            recommendation,
        )

    console.print(table)
    return load_balancers