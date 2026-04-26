import json
from functools import lru_cache

from rich.console import Console
from rich.table import Table

from aws_clients import client

console = Console()

HOURS_PER_MONTH = 730

AWS_REGION_LOCATION = {
    "us-east-1": "US East (N. Virginia)",
    "us-east-2": "US East (Ohio)",
    "us-west-1": "US West (N. California)",
    "us-west-2": "US West (Oregon)",
    "ca-central-1": "Canada (Central)",
    "eu-west-1": "EU (Ireland)",
    "eu-west-2": "EU (London)",
    "eu-central-1": "EU (Frankfurt)",
    "ap-southeast-1": "Asia Pacific (Singapore)",
    "ap-southeast-2": "Asia Pacific (Sydney)",
    "ap-northeast-1": "Asia Pacific (Tokyo)",
    "sa-east-1": "South America (Sao Paulo)",
    "mx-central-1": "Mexico (Central)",
}


def get_location(region: str) -> str:
    return AWS_REGION_LOCATION.get(region, region)


def extract_usd_price(price_item: dict):
    terms = price_item.get("terms", {}).get("OnDemand", {})

    for term in terms.values():
        for dimension in term.get("priceDimensions", {}).values():
            price_per_unit = dimension.get("pricePerUnit", {})
            usd = price_per_unit.get("USD")

            if usd is not None:
                price = float(usd)
                if price > 0:
                    return price

    return None


@lru_cache(maxsize=512)
def get_ec2_ondemand_hourly_price(
    profile: str,
    region: str,
    instance_type: str,
    operating_system: str = "Linux",
    tenancy: str = "Shared",
    pre_installed_sw: str = "NA",
    capacity_status: str = "Used",
):
    pricing = client("pricing", profile, "us-east-1")

    try:
        response = pricing.get_products(
            ServiceCode="AmazonEC2",
            Filters=[
                {
                    "Type": "TERM_MATCH",
                    "Field": "location",
                    "Value": get_location(region),
                },
                {
                    "Type": "TERM_MATCH",
                    "Field": "instanceType",
                    "Value": instance_type,
                },
                {
                    "Type": "TERM_MATCH",
                    "Field": "operatingSystem",
                    "Value": operating_system,
                },
                {
                    "Type": "TERM_MATCH",
                    "Field": "tenancy",
                    "Value": tenancy,
                },
                {
                    "Type": "TERM_MATCH",
                    "Field": "preInstalledSw",
                    "Value": pre_installed_sw,
                },
                {
                    "Type": "TERM_MATCH",
                    "Field": "capacitystatus",
                    "Value": capacity_status,
                },
            ],
            MaxResults=100,
        )
    except Exception:
        return None

    for item in response.get("PriceList", []):
        price_item = json.loads(item)
        price = extract_usd_price(price_item)

        if price:
            return price

    return None


@lru_cache(maxsize=512)
def get_ebs_monthly_gb_price(
    profile: str,
    region: str,
    volume_type: str,
):
    pricing = client("pricing", profile, "us-east-1")

    volume_api_to_pricing = {
        "gp2": "General Purpose",
        "gp3": "General Purpose",
        "io1": "Provisioned IOPS",
        "io2": "Provisioned IOPS",
        "st1": "Throughput Optimized HDD",
        "sc1": "Cold HDD",
        "standard": "Magnetic",
    }

    try:
        response = pricing.get_products(
            ServiceCode="AmazonEC2",
            Filters=[
                {
                    "Type": "TERM_MATCH",
                    "Field": "location",
                    "Value": get_location(region),
                },
                {
                    "Type": "TERM_MATCH",
                    "Field": "productFamily",
                    "Value": "Storage",
                },
                {
                    "Type": "TERM_MATCH",
                    "Field": "volumeType",
                    "Value": volume_api_to_pricing.get(volume_type, volume_type),
                },
            ],
            MaxResults=100,
        )
    except Exception:
        return None

    for item in response.get("PriceList", []):
        price_item = json.loads(item)
        attributes = price_item.get("product", {}).get("attributes", {})
        usage_type = attributes.get("usagetype", "").lower()

        if volume_type in usage_type or "gp3" in usage_type or "gp2" in usage_type:
            price = extract_usd_price(price_item)

            if price:
                return price

    return None


@lru_cache(maxsize=512)
def get_nat_gateway_hourly_price(profile: str, region: str):
    pricing = client("pricing", profile, "us-east-1")

    try:
        response = pricing.get_products(
            ServiceCode="AmazonVPC",
            Filters=[
                {
                    "Type": "TERM_MATCH",
                    "Field": "location",
                    "Value": get_location(region),
                },
                {
                    "Type": "TERM_MATCH",
                    "Field": "group",
                    "Value": "NGW:NatGateway",
                },
            ],
            MaxResults=100,
        )
    except Exception:
        return None

    for item in response.get("PriceList", []):
        price_item = json.loads(item)
        attributes = price_item.get("product", {}).get("attributes", {})
        operation = attributes.get("operation", "").lower()
        usage_type = attributes.get("usagetype", "").lower()

        if "natgateway-hours" in usage_type or "natgateway" in operation:
            price = extract_usd_price(price_item)

            if price:
                return price

    return None


def estimate_ec2_monthly_cost(profile: str, instance: dict):
    region = instance.get("region", "us-east-1")
    instance_type = instance.get("type")

    hourly = get_ec2_ondemand_hourly_price(
        profile=profile,
        region=region,
        instance_type=instance_type,
        operating_system="Linux",
    )

    if hourly is None:
        return 0.0

    return hourly * HOURS_PER_MONTH


def estimate_ebs_monthly_cost(profile: str, volume: dict):
    region = volume.get("region", "us-east-1")
    volume_type = volume.get("type")
    size_gb = volume.get("size", 0)

    gb_price = get_ebs_monthly_gb_price(
        profile=profile,
        region=region,
        volume_type=volume_type,
    )

    if gb_price is None:
        return 0.0

    return gb_price * size_gb


def estimate_nat_monthly_base_cost(profile: str, nat: dict):
    region = nat.get("region", "us-east-1")

    hourly = get_nat_gateway_hourly_price(
        profile=profile,
        region=region,
    )

    if hourly is None:
        return 0.0

    return hourly * HOURS_PER_MONTH


def estimate_savings(report: dict):
    profile = report.get("profile", "default")

    ec2 = report.get("ec2_instances", [])
    ebs = report.get("ebs_volumes", [])
    eips = report.get("elastic_ips", [])
    nat = report.get("nat_gateways", [])

    total_waste = 0.0

    table = Table(title="Estimated Monthly Savings / Cost Exposure")
    table.add_column("Resource", style="cyan")
    table.add_column("Region")
    table.add_column("ID")
    table.add_column("Est. Monthly Cost USD", justify="right")
    table.add_column("Pricing Source")
    table.add_column("Action", style="bold")

    for instance in ec2:
        if "TERMINATE" in instance.get("recommendation", ""):
            cost = estimate_ec2_monthly_cost(profile, instance)
            total_waste += cost

            table.add_row(
                "EC2",
                instance.get("region", "N/A"),
                instance.get("id", "N/A"),
                f"${cost:,.2f}",
                "AWS Price List API",
                "[red]Stop/Terminate Candidate[/red]",
            )

    for volume in ebs:
        if "DELETE" in volume.get("recommendation", ""):
            cost = estimate_ebs_monthly_cost(profile, volume)
            total_waste += cost

            table.add_row(
                "EBS",
                volume.get("region", "N/A"),
                volume.get("id", "N/A"),
                f"${cost:,.2f}",
                "AWS Price List API",
                "[red]Delete Candidate[/red]",
            )

    for ip in eips:
        if "RELEASE" in ip.get("recommendation", ""):
            table.add_row(
                "Elastic IP",
                ip.get("region", "N/A"),
                ip.get("public_ip", "N/A"),
                "Use Cost Explorer",
                "Cost Explorer",
                "[red]Release Unused EIP[/red]",
            )

    for gateway in nat:
        if "VERIFY" in gateway.get("recommendation", ""):
            cost = estimate_nat_monthly_base_cost(profile, gateway)
            total_waste += cost

            table.add_row(
                "NAT Gateway",
                gateway.get("region", "N/A"),
                gateway.get("id", "N/A"),
                f"${cost:,.2f} + traffic",
                "AWS Price List API + CloudWatch",
                "[yellow]Validate Traffic[/yellow]",
            )

    console.print(table)

    console.print(
        f"\n[bold green]Estimated Monthly Savings / Cost Exposure: ${total_waste:,.2f} USD[/bold green]"
    )

    return total_waste