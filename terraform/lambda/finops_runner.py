import json
import os
from datetime import datetime, timedelta, timezone
from decimal import Decimal

import boto3


s3 = boto3.client("s3")
sns = boto3.client("sns")
sts = boto3.client("sts")
ec2 = boto3.client("ec2")
cloudwatch = boto3.client("cloudwatch")


CPU_IDLE_THRESHOLD = float(os.environ.get("CPU_IDLE_THRESHOLD", "5"))
CPU_RIGHTSIZE_THRESHOLD = float(os.environ.get("CPU_RIGHTSIZE_THRESHOLD", "20"))
METRIC_LOOKBACK_DAYS = int(os.environ.get("METRIC_LOOKBACK_DAYS", "7"))

MONTHLY_HOURS = float(os.environ.get("MONTHLY_HOURS", "730"))

DEFAULT_EC2_HOURLY_RATE = float(os.environ.get("DEFAULT_EC2_HOURLY_RATE", "0.05"))
RIGHTSIZE_SAVINGS_FACTOR = float(os.environ.get("RIGHTSIZE_SAVINGS_FACTOR", "0.30"))

EBS_GP2_GB_MONTH_RATE = float(os.environ.get("EBS_GP2_GB_MONTH_RATE", "0.10"))
EBS_GP3_GB_MONTH_RATE = float(os.environ.get("EBS_GP3_GB_MONTH_RATE", "0.08"))

PUBLIC_IPV4_HOURLY_RATE = float(os.environ.get("PUBLIC_IPV4_HOURLY_RATE", "0.005"))


def json_safe(value):
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    return str(value)


def get_name_tag(tags):
    if not tags:
        return None

    for tag in tags:
        if tag.get("Key") == "Name":
            return tag.get("Value")

    return None


def get_tag_value(tags, key):
    if not tags:
        return None

    for tag in tags:
        if tag.get("Key") == key:
            return tag.get("Value")

    return None


def estimate_monthly_ec2_cost(instance_type=None):
    return round(DEFAULT_EC2_HOURLY_RATE * MONTHLY_HOURS, 2)


def estimate_idle_ec2_savings(instance_type=None):
    return round(estimate_monthly_ec2_cost(instance_type), 2)


def estimate_rightsize_savings(instance_type=None):
    estimated_monthly_cost = estimate_monthly_ec2_cost(instance_type)
    return round(estimated_monthly_cost * RIGHTSIZE_SAVINGS_FACTOR, 2)


def estimate_ebs_monthly_cost(size_gib, volume_type):
    if volume_type == "gp3":
        rate = EBS_GP3_GB_MONTH_RATE
    else:
        rate = EBS_GP2_GB_MONTH_RATE

    return round(float(size_gib or 0) * rate, 2)


def estimate_gp2_to_gp3_savings(size_gib):
    gp2_cost = float(size_gib or 0) * EBS_GP2_GB_MONTH_RATE
    gp3_cost = float(size_gib or 0) * EBS_GP3_GB_MONTH_RATE
    return round(max(gp2_cost - gp3_cost, 0), 2)


def estimate_public_ipv4_monthly_cost():
    return round(PUBLIC_IPV4_HOURLY_RATE * MONTHLY_HOURS, 2)


def add_cost_impact(finding, estimated_monthly_savings, confidence, pricing_model, assumptions):
    finding["cost_impact"] = {
        "currency": "USD",
        "estimated_monthly_savings": round(float(estimated_monthly_savings), 2),
        "estimated_annual_savings": round(float(estimated_monthly_savings) * 12, 2),
        "confidence": confidence,
        "pricing_model": pricing_model,
        "assumptions": assumptions,
    }

    return finding


def get_average_cpu_utilization(instance_id):
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(days=METRIC_LOOKBACK_DAYS)

    response = cloudwatch.get_metric_statistics(
        Namespace="AWS/EC2",
        MetricName="CPUUtilization",
        Dimensions=[
            {
                "Name": "InstanceId",
                "Value": instance_id,
            }
        ],
        StartTime=start_time,
        EndTime=end_time,
        Period=86400,
        Statistics=["Average"],
    )

    datapoints = response.get("Datapoints", [])

    if not datapoints:
        return None

    average = sum(point["Average"] for point in datapoints) / len(datapoints)

    return round(average, 2)


def scan_ec2_instances():
    findings = []
    resources = []

    paginator = ec2.get_paginator("describe_instances")

    for page in paginator.paginate():
        for reservation in page.get("Reservations", []):
            for instance in reservation.get("Instances", []):
                instance_id = instance.get("InstanceId")
                instance_type = instance.get("InstanceType")
                state = instance.get("State", {}).get("Name")
                launch_time = instance.get("LaunchTime")
                tags = instance.get("Tags", [])

                name = get_name_tag(tags)
                owner = get_tag_value(tags, "Owner")
                cost_center = get_tag_value(tags, "CostCenter")
                environment = get_tag_value(tags, "Environment")

                estimated_monthly_cost = estimate_monthly_ec2_cost(instance_type)

                resource = {
                    "resource_type": "ec2_instance",
                    "resource_id": instance_id,
                    "name": name,
                    "instance_type": instance_type,
                    "state": state,
                    "launch_time": launch_time,
                    "owner": owner,
                    "cost_center": cost_center,
                    "environment": environment,
                    "estimated_monthly_cost_usd": estimated_monthly_cost,
                }

                if state == "running":
                    avg_cpu = get_average_cpu_utilization(instance_id)
                    resource["average_cpu_7d"] = avg_cpu

                    if avg_cpu is None:
                        finding = {
                            "resource_type": "ec2_instance",
                            "resource_id": instance_id,
                            "severity": "medium",
                            "category": "observability_gap",
                            "finding": "No CloudWatch CPU datapoints found for the lookback period.",
                            "recommendation": "Validate monitoring coverage before making optimization decisions.",
                            "risk": "Insufficient utilization evidence.",
                            "automation_policy": "manual_review_required",
                        }

                        finding = add_cost_impact(
                            finding=finding,
                            estimated_monthly_savings=0,
                            confidence="low",
                            pricing_model="no_savings_estimated_without_utilization_evidence",
                            assumptions=[
                                "No CPU datapoints were found.",
                                "No savings estimate is assigned until utilization evidence exists.",
                            ],
                        )

                        findings.append(finding)

                    elif avg_cpu < CPU_IDLE_THRESHOLD:
                        finding = {
                            "resource_type": "ec2_instance",
                            "resource_id": instance_id,
                            "severity": "high",
                            "category": "idle_compute",
                            "finding": f"Average CPU utilization is {avg_cpu}% over the last {METRIC_LOOKBACK_DAYS} days.",
                            "recommendation": "Review workload ownership. If non-production or unused, stop or terminate after validation.",
                            "risk": "Potential recurring compute waste.",
                            "automation_policy": "non_destructive_recommendation",
                        }

                        finding = add_cost_impact(
                            finding=finding,
                            estimated_monthly_savings=estimate_idle_ec2_savings(instance_type),
                            confidence="medium",
                            pricing_model="default_ec2_hourly_rate_x_monthly_hours",
                            assumptions=[
                                f"Default EC2 hourly rate: ${DEFAULT_EC2_HOURLY_RATE}/hour.",
                                f"Monthly hours: {MONTHLY_HOURS}.",
                                "This is a conservative placeholder until AWS Price List API integration is added.",
                                "Actual savings depend on instance type, region, purchase option, and workload validation.",
                            ],
                        )

                        findings.append(finding)

                    elif avg_cpu < CPU_RIGHTSIZE_THRESHOLD:
                        finding = {
                            "resource_type": "ec2_instance",
                            "resource_id": instance_id,
                            "severity": "medium",
                            "category": "rightsizing_candidate",
                            "finding": f"Average CPU utilization is {avg_cpu}% over the last {METRIC_LOOKBACK_DAYS} days.",
                            "recommendation": "Evaluate smaller instance type or autoscaling policy.",
                            "risk": "Potential overprovisioned compute.",
                            "automation_policy": "non_destructive_recommendation",
                        }

                        finding = add_cost_impact(
                            finding=finding,
                            estimated_monthly_savings=estimate_rightsize_savings(instance_type),
                            confidence="low",
                            pricing_model="estimated_monthly_ec2_cost_x_rightsize_savings_factor",
                            assumptions=[
                                f"Default EC2 hourly rate: ${DEFAULT_EC2_HOURLY_RATE}/hour.",
                                f"Rightsizing savings factor: {RIGHTSIZE_SAVINGS_FACTOR}.",
                                "Actual savings require AWS Compute Optimizer, instance family mapping, or Price List API.",
                            ],
                        )

                        findings.append(finding)

                elif state == "stopped":
                    finding = {
                        "resource_type": "ec2_instance",
                        "resource_id": instance_id,
                        "severity": "medium",
                        "category": "stopped_instance",
                        "finding": "EC2 instance is stopped but may still have attached EBS volumes generating cost.",
                        "recommendation": "Validate business ownership and attached volumes. Terminate only after backup and approval.",
                        "risk": "Stopped compute may hide persistent storage cost.",
                        "automation_policy": "manual_review_required",
                    }

                    finding = add_cost_impact(
                        finding=finding,
                        estimated_monthly_savings=0,
                        confidence="low",
                        pricing_model="no_compute_savings_for_stopped_instance",
                        assumptions=[
                            "Stopped EC2 instances do not generate running compute charges.",
                            "Storage cost is estimated separately through attached or orphaned EBS volumes.",
                        ],
                    )

                    findings.append(finding)

                resources.append(resource)

    return resources, findings


def scan_ebs_volumes():
    findings = []
    resources = []

    paginator = ec2.get_paginator("describe_volumes")

    for page in paginator.paginate():
        for volume in page.get("Volumes", []):
            volume_id = volume.get("VolumeId")
            state = volume.get("State")
            volume_type = volume.get("VolumeType")
            size = volume.get("Size")
            encrypted = volume.get("Encrypted")
            az = volume.get("AvailabilityZone")
            create_time = volume.get("CreateTime")
            attachments = volume.get("Attachments", [])
            tags = volume.get("Tags", [])

            name = get_name_tag(tags)
            owner = get_tag_value(tags, "Owner")
            cost_center = get_tag_value(tags, "CostCenter")
            environment = get_tag_value(tags, "Environment")

            estimated_monthly_cost = estimate_ebs_monthly_cost(size, volume_type)

            resource = {
                "resource_type": "ebs_volume",
                "resource_id": volume_id,
                "name": name,
                "state": state,
                "volume_type": volume_type,
                "size_gib": size,
                "encrypted": encrypted,
                "availability_zone": az,
                "create_time": create_time,
                "attachment_count": len(attachments),
                "owner": owner,
                "cost_center": cost_center,
                "environment": environment,
                "estimated_monthly_cost_usd": estimated_monthly_cost,
            }

            if state == "available":
                finding = {
                    "resource_type": "ebs_volume",
                    "resource_id": volume_id,
                    "severity": "high",
                    "category": "orphaned_storage",
                    "finding": f"EBS volume is available/unattached. Size: {size} GiB.",
                    "recommendation": "Create snapshot if required, validate ownership, then delete if no longer needed.",
                    "risk": "Direct recurring storage waste.",
                    "automation_policy": "manual_approval_required",
                }

                finding = add_cost_impact(
                    finding=finding,
                    estimated_monthly_savings=estimated_monthly_cost,
                    confidence="medium",
                    pricing_model="volume_size_gib_x_ebs_gb_month_rate",
                    assumptions=[
                        f"Volume type: {volume_type}.",
                        f"Volume size: {size} GiB.",
                        f"Estimated EBS monthly rate used: ${EBS_GP2_GB_MONTH_RATE}/GB-month for gp2 or ${EBS_GP3_GB_MONTH_RATE}/GB-month for gp3.",
                        "Snapshot cost is not included.",
                        "Deletion requires backup and ownership validation.",
                    ],
                )

                findings.append(finding)

            if volume_type == "gp2":
                migration_savings = estimate_gp2_to_gp3_savings(size)

                finding = {
                    "resource_type": "ebs_volume",
                    "resource_id": volume_id,
                    "severity": "medium",
                    "category": "storage_modernization",
                    "finding": f"EBS volume uses gp2. Size: {size} GiB.",
                    "recommendation": "Evaluate migration to gp3 for cost/performance optimization.",
                    "risk": "Legacy EBS type may be less cost-efficient than gp3.",
                    "automation_policy": "non_destructive_recommendation",
                }

                finding = add_cost_impact(
                    finding=finding,
                    estimated_monthly_savings=migration_savings,
                    confidence="medium",
                    pricing_model="gp2_monthly_cost_minus_gp3_monthly_cost",
                    assumptions=[
                        f"gp2 rate used: ${EBS_GP2_GB_MONTH_RATE}/GB-month.",
                        f"gp3 rate used: ${EBS_GP3_GB_MONTH_RATE}/GB-month.",
                        "Additional gp3 IOPS or throughput charges are not included.",
                        "Migration requires performance validation.",
                    ],
                )

                findings.append(finding)

            if encrypted is False:
                finding = {
                    "resource_type": "ebs_volume",
                    "resource_id": volume_id,
                    "severity": "medium",
                    "category": "security_governance",
                    "finding": "EBS volume is not encrypted.",
                    "recommendation": "Review encryption requirements and migrate to encrypted volume if required.",
                    "risk": "Security and compliance exposure.",
                    "automation_policy": "manual_review_required",
                }

                finding = add_cost_impact(
                    finding=finding,
                    estimated_monthly_savings=0,
                    confidence="not_applicable",
                    pricing_model="security_finding_no_direct_savings",
                    assumptions=[
                        "Encryption finding is treated as governance risk, not direct cost savings.",
                    ],
                )

                findings.append(finding)

            resources.append(resource)

    return resources, findings


def scan_elastic_ips():
    findings = []
    resources = []

    response = ec2.describe_addresses()

    for address in response.get("Addresses", []):
        allocation_id = address.get("AllocationId")
        public_ip = address.get("PublicIp")
        association_id = address.get("AssociationId")
        instance_id = address.get("InstanceId")
        network_interface_id = address.get("NetworkInterfaceId")
        tags = address.get("Tags", [])

        name = get_name_tag(tags)
        owner = get_tag_value(tags, "Owner")
        cost_center = get_tag_value(tags, "CostCenter")
        environment = get_tag_value(tags, "Environment")

        resource_id = allocation_id or public_ip
        estimated_monthly_cost = estimate_public_ipv4_monthly_cost()

        resource = {
            "resource_type": "elastic_ip",
            "resource_id": resource_id,
            "public_ip": public_ip,
            "association_id": association_id,
            "instance_id": instance_id,
            "network_interface_id": network_interface_id,
            "name": name,
            "owner": owner,
            "cost_center": cost_center,
            "environment": environment,
            "estimated_monthly_cost_usd": estimated_monthly_cost,
        }

        if not association_id:
            finding = {
                "resource_type": "elastic_ip",
                "resource_id": resource_id,
                "severity": "high",
                "category": "unused_network_resource",
                "finding": f"Elastic IP {public_ip} is not associated with any resource.",
                "recommendation": "Release Elastic IP after confirming it is not reserved for a known workload.",
                "risk": "Direct recurring network waste.",
                "automation_policy": "manual_approval_required",
            }

            finding = add_cost_impact(
                finding=finding,
                estimated_monthly_savings=estimated_monthly_cost,
                confidence="high",
                pricing_model="public_ipv4_hourly_rate_x_monthly_hours",
                assumptions=[
                    f"Public IPv4 hourly rate used: ${PUBLIC_IPV4_HOURLY_RATE}/hour.",
                    f"Monthly hours: {MONTHLY_HOURS}.",
                    "AWS charges for public IPv4 addresses whether in-use or idle.",
                    "Release requires ownership validation.",
                ],
            )

            findings.append(finding)

        resources.append(resource)

    return resources, findings


def summarize_findings(findings):
    summary = {
        "total_findings": len(findings),
        "by_severity": {
            "high": 0,
            "medium": 0,
            "low": 0,
        },
        "by_category": {},
        "estimated_monthly_savings_usd": 0,
        "estimated_annual_savings_usd": 0,
    }

    for finding in findings:
        severity = finding.get("severity", "low")
        category = finding.get("category", "uncategorized")
        monthly_savings = finding.get("cost_impact", {}).get("estimated_monthly_savings", 0)

        summary["by_severity"][severity] = summary["by_severity"].get(severity, 0) + 1
        summary["by_category"][category] = summary["by_category"].get(category, 0) + 1
        summary["estimated_monthly_savings_usd"] += float(monthly_savings)

    summary["estimated_monthly_savings_usd"] = round(summary["estimated_monthly_savings_usd"], 2)
    summary["estimated_annual_savings_usd"] = round(summary["estimated_monthly_savings_usd"] * 12, 2)

    return summary


def lambda_handler(event, context):
    report_bucket = os.environ["FINOPS_REPORT_BUCKET"]
    sns_topic_arn = os.environ["FINOPS_SNS_TOPIC_ARN"]
    project_name = os.environ.get("PROJECT_NAME", "aws-finops-control-tower")
    environment = os.environ.get("ENVIRONMENT", "dev")

    execution_time = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")
    execution_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    account_identity = sts.get_caller_identity()

    ec2_resources, ec2_findings = scan_ec2_instances()
    ebs_resources, ebs_findings = scan_ebs_volumes()
    eip_resources, eip_findings = scan_elastic_ips()

    resources = ec2_resources + ebs_resources + eip_resources
    findings = ec2_findings + ebs_findings + eip_findings
    summary = summarize_findings(findings)

    report = {
        "project": project_name,
        "environment": environment,
        "execution_time_utc": execution_time,
        "account_id": account_identity.get("Account"),
        "caller_arn": account_identity.get("Arn"),
        "mode": "finops_cost_impact_estimation",
        "automation_policy": "non_destructive",
        "scope": [
            "ec2_instances",
            "ebs_volumes",
            "elastic_ips",
            "cloudwatch_cpu_metrics",
            "monthly_cost_impact_estimation",
        ],
        "pricing_assumptions": {
            "monthly_hours": MONTHLY_HOURS,
            "default_ec2_hourly_rate": DEFAULT_EC2_HOURLY_RATE,
            "rightsize_savings_factor": RIGHTSIZE_SAVINGS_FACTOR,
            "ebs_gp2_gb_month_rate": EBS_GP2_GB_MONTH_RATE,
            "ebs_gp3_gb_month_rate": EBS_GP3_GB_MONTH_RATE,
            "public_ipv4_hourly_rate": PUBLIC_IPV4_HOURLY_RATE,
        },
        "summary": summary,
        "resource_count": len(resources),
        "resources": resources,
        "findings": findings,
        "event": event,
    }

    report_key = f"reports/finops-cost-impact/date={execution_date}/{execution_time}.json"

    s3.put_object(
        Bucket=report_bucket,
        Key=report_key,
        Body=json.dumps(report, indent=2, default=json_safe),
        ContentType="application/json",
    )

    high = summary["by_severity"].get("high", 0)
    medium = summary["by_severity"].get("medium", 0)
    monthly_savings = summary["estimated_monthly_savings_usd"]
    annual_savings = summary["estimated_annual_savings_usd"]

    sns_message = (
        "AWS FinOps Control Tower cost impact estimation completed.\n\n"
        f"Project: {project_name}\n"
        f"Environment: {environment}\n"
        f"Account: {account_identity.get('Account')}\n"
        f"Execution Time UTC: {execution_time}\n\n"
        f"Resources Scanned: {len(resources)}\n"
        f"Total Findings: {summary['total_findings']}\n"
        f"High Severity: {high}\n"
        f"Medium Severity: {medium}\n\n"
        f"Estimated Monthly Savings: ${monthly_savings} USD\n"
        f"Estimated Annual Savings: ${annual_savings} USD\n\n"
        f"Report: s3://{report_bucket}/{report_key}\n\n"
        "Policy: non-destructive recommendations only."
    )

    sns.publish(
        TopicArn=sns_topic_arn,
        Subject=f"AWS FinOps Cost Impact - ${monthly_savings}/mo Estimated",
        Message=sns_message,
    )

    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "status": "success",
                "mode": "finops_cost_impact_estimation",
                "resource_count": len(resources),
                "total_findings": summary["total_findings"],
                "high_findings": high,
                "medium_findings": medium,
                "estimated_monthly_savings_usd": monthly_savings,
                "estimated_annual_savings_usd": annual_savings,
                "report_bucket": report_bucket,
                "report_key": report_key,
            }
        ),
    }
