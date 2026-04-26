from datetime import datetime, timedelta, timezone
from aws_clients import client


def get_ec2_avg_cpu(
    profile: str,
    region: str,
    instance_id: str,
    days: int = 7
):
    cw = client("cloudwatch", profile, region)

    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(days=days)

    response = cw.get_metric_statistics(
        Namespace="AWS/EC2",
        MetricName="CPUUtilization",
        Dimensions=[
            {
                "Name": "InstanceId",
                "Value": instance_id
            }
        ],
        StartTime=start_time,
        EndTime=end_time,
        Period=86400,
        Statistics=["Average"]
    )

    datapoints = response.get("Datapoints", [])

    if not datapoints:
        return None

    avg_cpu = sum(point["Average"] for point in datapoints) / len(datapoints)

    return round(avg_cpu, 2)