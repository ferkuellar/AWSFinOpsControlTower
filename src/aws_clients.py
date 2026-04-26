import boto3


def session(profile: str = "default", region: str = "us-east-1"):
    return boto3.Session(
        profile_name=profile,
        region_name=region
    )


def client(service: str, profile: str = "default", region: str = "us-east-1"):
    aws_session = session(profile, region)
    return aws_session.client(service)


def global_client(service: str, profile: str = "default"):
    aws_session = boto3.Session(profile_name=profile)
    return aws_session.client(service)