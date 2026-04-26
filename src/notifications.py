from rich.console import Console

from aws_clients import client

console = Console()


def publish_sns_alert(
    profile: str,
    region: str,
    topic_arn: str,
    subject: str,
    message: str,
):
    sns = client("sns", profile, region)

    try:
        response = sns.publish(
            TopicArn=topic_arn,
            Subject=subject,
            Message=message,
        )

        console.print(
            f"[green]SNS alert sent successfully:[/green] {response.get('MessageId')}"
        )

        return response

    except Exception as error:
        console.print(f"[red]Failed to publish SNS alert:[/red] {error}")
        return None


def build_finops_alert_message(
    report: dict,
    total_savings: float,
    consolidated_file: str,
):
    cost_summary = report.get("cost_summary", {})

    ec2 = report.get("ec2_instances", [])
    ebs = report.get("ebs_volumes", [])
    eips = report.get("elastic_ips", [])
    nat = report.get("nat_gateways", [])
    s3 = report.get("s3_buckets", [])
    rds = report.get("rds_instances", [])
    lambdas = report.get("lambda_functions", [])

    terminate_candidates = sum(
        1 for item in ec2
        if "TERMINATE" in str(item.get("recommendation", "")).upper()
    )

    rightsizing_candidates = sum(
        1 for item in ec2
        if "RIGHTSIZE" in str(item.get("recommendation", "")).upper()
    )

    unattached_ebs = sum(
        1 for item in ebs
        if "DELETE" in str(item.get("recommendation", "")).upper()
    )

    unused_eips = sum(
        1 for item in eips
        if "RELEASE" in str(item.get("recommendation", "")).upper()
    )

    nat_review = sum(
        1 for item in nat
        if "VERIFY" in str(item.get("recommendation", "")).upper()
    )

    s3_lifecycle = sum(
        1 for item in s3
        if "LIFECYCLE" in str(item.get("recommendation", "")).upper()
    )

    rds_review = sum(
        1 for item in rds
        if "REVIEW" in str(item.get("recommendation", "")).upper()
    )

    lambda_review = sum(
        1 for item in lambdas
        if "REVIEW" in str(item.get("recommendation", "")).upper()
    )

    message = f"""
AWS FinOps Control Tower Alert

Profile:
{report.get("profile")}

Regions:
{", ".join(report.get("regions", []))}

Cost Period:
{cost_summary.get("start", "N/A")} to {cost_summary.get("end", "N/A")}

Monthly Spend Detected:
${cost_summary.get("total", 0):,.2f} USD

Estimated Monthly Savings / Exposure:
${total_savings:,.2f} USD

High-Impact Findings:
- EC2 stop/terminate candidates: {terminate_candidates}
- Unattached EBS volumes: {unattached_ebs}
- Unused Elastic IPs: {unused_eips}

Optimization Findings:
- EC2 rightsizing candidates: {rightsizing_candidates}
- NAT Gateway review items: {nat_review}
- S3 lifecycle policy findings: {s3_lifecycle}
- RDS review items: {rds_review}
- Lambda tuning items: {lambda_review}

Generated Report:
{consolidated_file}

Recommended Next Step:
Validate ownership, backup status, production impact, and rollback path before applying any remediation.

FinOps Control Tower
"""
    return message.strip()