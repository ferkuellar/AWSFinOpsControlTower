import json
import os
from datetime import datetime, timezone

import boto3


s3 = boto3.client("s3")
sns = boto3.client("sns")
sts = boto3.client("sts")


def lambda_handler(event, context):
    """
    AWS FinOps Control Tower - Execution Layer

    This function is intentionally non-destructive.
    It creates an execution report, stores it in S3, and sends an SNS alert.

    Future phases will call the real FinOps discovery and decision engine.
    """

    report_bucket = os.environ["FINOPS_REPORT_BUCKET"]
    sns_topic_arn = os.environ["FINOPS_SNS_TOPIC_ARN"]
    project_name = os.environ.get("PROJECT_NAME", "aws-finops-control-tower")
    environment = os.environ.get("ENVIRONMENT", "dev")

    execution_time = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    account_identity = sts.get_caller_identity()

    report = {
        "project": project_name,
        "environment": environment,
        "execution_time_utc": execution_time,
        "account_id": account_identity.get("Account"),
        "caller_arn": account_identity.get("Arn"),
        "mode": "safe_execution_validation",
        "automation_policy": "non_destructive",
        "status": "success",
        "message": "FinOps execution layer validated successfully. No infrastructure changes were performed.",
        "event": event,
    }

    report_key = f"reports/execution-validation/{execution_time}.json"

    s3.put_object(
        Bucket=report_bucket,
        Key=report_key,
        Body=json.dumps(report, indent=2),
        ContentType="application/json",
    )

    sns_message = (
        "AWS FinOps Control Tower execution completed.\n\n"
        f"Project: {project_name}\n"
        f"Environment: {environment}\n"
        f"Account: {account_identity.get('Account')}\n"
        f"Execution Time UTC: {execution_time}\n"
        f"Report: s3://{report_bucket}/{report_key}\n\n"
        "Mode: non-destructive validation."
    )

    sns.publish(
        TopicArn=sns_topic_arn,
        Subject="AWS FinOps Control Tower - Execution Completed",
        Message=sns_message,
    )

    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "status": "success",
                "report_bucket": report_bucket,
                "report_key": report_key,
            }
        ),
    }
