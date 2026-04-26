from aws_clients import client


def get_enabled_regions(profile: str):
    ec2 = client("ec2", profile, "us-east-1")

    response = ec2.describe_regions(
        AllRegions=False
    )

    return [region["RegionName"] for region in response["Regions"]]