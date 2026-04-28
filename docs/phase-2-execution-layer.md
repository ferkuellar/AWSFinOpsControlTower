# Phase 2 - Execution Layer

## Objective

This phase implements the scheduled execution layer for the AWS FinOps Control Tower.

The platform now includes a serverless execution model that allows the FinOps process to run on a defined schedule, generate an execution report, persist the report in S3, publish an SNS notification, and leave an audit trail in CloudWatch Logs.

This phase does not perform optimization actions. It validates that the operational pipeline is working correctly.

---

## Architecture

EventBridge Schedule
        |
        v
Lambda FinOps Runner
        |
        |-- Generate execution report
        |-- Store JSON report in S3
        |-- Publish SNS alert
        |-- Write logs to CloudWatch

---

## Components Implemented

| Component        | Purpose                                    |
| ---------------- | ------------------------------------------ |
| AWS Lambda       | Runs the FinOps execution layer            |
| EventBridge Rule | Triggers the Lambda function on a schedule |
| S3 Bucket        | Stores generated execution reports         |
| SNS Topic        | Sends alert notifications                  |
| IAM Role         | Grants controlled execution permissions    |
| CloudWatch Logs  | Stores execution logs for auditability     |

---

## Execution Flow

1. EventBridge triggers the Lambda function based on the configured schedule.
2. Lambda collects basic execution context.
3. Lambda validates the AWS caller identity.
4. Lambda generates a non-destructive execution report.
5. The report is written to the configured S3 bucket.
6. Lambda publishes a notification to the SNS topic.
7. Execution logs are written to CloudWatch Logs.

---

## Safety Model

This phase is intentionally non-destructive.

The Lambda function does not:

- Delete resources
- Stop EC2 instances
- Modify infrastructure
- Apply recommendations automatically
- Change storage classes
- Release Elastic IPs
- Resize compute resources

The purpose of this phase is to validate the execution pipeline, not to perform remediation.

---

## Non-Destructive Execution Policy

The system follows this operating principle:

Detect first.
Report second.
Notify third.
Execute only after governance approval.

This supports a controlled FinOps operating model where recommendations must pass ownership validation, environment classification, backup verification, business impact analysis, rollback planning, and approval before execution.

---

## Terraform Resources Added

This phase adds the following Terraform-managed resources:

- aws_lambda_function.finops_runner
- aws_cloudwatch_log_group.finops_lambda_logs
- aws_cloudwatch_event_rule.finops_schedule
- aws_cloudwatch_event_target.finops_lambda_target
- aws_lambda_permission.allow_eventbridge_to_invoke_finops_lambda
- data.archive_file.finops_lambda_package

---

## Lambda Runtime

The Lambda function uses Python as the execution runtime.

Function entry point:

finops_runner.lambda_handler

Source file:

terraform/lambda/finops_runner.py

Packaged artifact:

terraform/lambda/finops_runner.zip

---

## Environment Variables

The Lambda function receives the following environment variables:

| Variable             | Description                            |
| -------------------- | -------------------------------------- |
| FINOPS_REPORT_BUCKET | S3 bucket where reports are stored     |
| FINOPS_SNS_TOPIC_ARN | SNS topic used for alert notifications |
| PROJECT_NAME         | Project identifier                     |
| ENVIRONMENT          | Deployment environment                 |

---

## Report Output

Reports are stored in S3 using the following prefix:

reports/execution-validation/

Example report path:

s3://`<finops-report-bucket>`/reports/execution-validation/`<timestamp>`.json

---

## SNS Notification

After each execution, the Lambda function publishes an SNS notification with:

- Project name
- Environment
- AWS account ID
- Execution timestamp
- S3 report location
- Execution mode

Current execution mode:

non-destructive validation

---

## EventBridge Schedule

The schedule is controlled through Terraform using:

var.finops_schedule_expression

Default value:

cron(0 13 * * ? *)

This means the FinOps runner is triggered every day at 13:00 UTC.

---

## Validation Commands

Validate Terraform:

terraform validate

View Terraform outputs:

terraform output

Invoke Lambda manually:

aws lambda invoke --function-name aws-finops-control-tower-dev-runner --payload "{\"manual_test\":true,\"phase\":\"phase-2\"}" --cli-binary-format raw-in-base64-out --profile ControlTower --region us-east-1 lambda-response.json

Validate EventBridge rule:

aws events describe-rule --name aws-finops-control-tower-dev-schedule --profile ControlTower --region us-east-1

Validate EventBridge targets:

aws events list-targets-by-rule --rule aws-finops-control-tower-dev-schedule --profile ControlTower --region us-east-1

Validate Lambda:

aws lambda get-function --function-name aws-finops-control-tower-dev-runner --profile ControlTower --region us-east-1

Validate CloudWatch Log Group:

aws logs describe-log-groups --log-group-name-prefix "/aws/lambda/aws-finops-control-tower-dev-runner" --profile ControlTower --region us-east-1

---

## Evidence Location

Evidence for this phase should be stored under:

docs/evidence/phase-2/

Expected evidence files:

- terraform-validate.txt
- terraform-outputs.txt
- lambda-function.txt
- eventbridge-rule.txt
- eventbridge-targets.txt
- lambda-response.json

---

## Business Value

This phase converts the FinOps engine from a manual execution model into a scheduled operational control.

It enables:

- Repeatable execution
- Scheduled FinOps validation
- Report persistence
- Alert-based visibility
- Audit-ready evidence
- Future integration with real cost and inventory analysis
- Clear separation between detection, reporting, and remediation

---

## Interview Positioning

This phase can be explained as:

I implemented a scheduled AWS FinOps execution layer using Terraform, Lambda, EventBridge, S3, SNS, IAM, and CloudWatch Logs. The system runs in non-destructive mode, generates auditable execution reports, stores them in S3, and notifies stakeholders through SNS. This provides the operational foundation for a controlled FinOps decision framework.

---

## Current State After Phase 2

AWS FinOps Control Tower
|
|-- Terraform Foundation
|   |-- S3 report bucket
|   |-- SNS alerting topic
|   |-- IAM execution role
|   |-- CloudWatch log groups
|
|-- Execution Layer
    |-- Lambda runner
    |-- EventBridge scheduled trigger
    |-- S3 JSON report output
    |-- SNS notification
    |-- CloudWatch audit trail

---
