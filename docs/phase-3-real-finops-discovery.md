# Phase 3 - Real FinOps Discovery Engine

## Objective

This phase integrates the first real FinOps discovery engine into the AWS FinOps Control Tower.

The Lambda function now scans:

- EC2 instances
- EBS volumes
- Elastic IPs
- CloudWatch CPU utilization metrics

## Execution Model

EventBridge
   |
   v
Lambda FinOps Runner
   |
   |-- Scan EC2 instances
   |-- Analyze CloudWatch CPU metrics
   |-- Scan EBS volumes
   |-- Scan Elastic IPs
   |-- Generate findings
   |-- Store JSON report in S3
   |-- Publish SNS executive summary

## Detection Rules

| Resource | Condition | Severity | Recommendation |
|---|---|---|---|
| EC2 | Running with CPU below 5% | High | Review, stop, terminate, or rightsize |
| EC2 | Running with CPU between 5% and 20% | Medium | Evaluate rightsizing |
| EC2 | Stopped instance | Medium | Review attached EBS and ownership |
| EBS | Available/unattached | High | Snapshot if required, then delete after approval |
| EBS | gp2 volume | Medium | Evaluate migration to gp3 |
| EBS | Unencrypted volume | Medium | Review encryption requirements |
| EIP | No association | High | Release after validation |

## Safety Model

This phase is non-destructive.

The system does not:

- Stop EC2 instances
- Terminate EC2 instances
- Delete EBS volumes
- Release Elastic IPs
- Modify infrastructure
- Apply recommendations automatically

All outputs are recommendations that require:

1. Ownership validation
2. Backup verification
3. Business impact review
4. Approval
5. Rollback planning

## Report Location

Reports are stored in S3 using the following prefix:

reports/finops-discovery/

## Evidence

Validation evidence is stored under:

docs/evidence/phase-3/

Expected evidence files:

- terraform-validate.txt
- terraform-outputs.txt
- phase-3-response.json
- s3-finops-discovery-reports.txt
- lambda-log-groups.txt
- reports/

## Business Value

This phase moves the platform from execution validation into real FinOps visibility.

It provides:

- Inventory awareness
- Utilization-based recommendations
- Waste detection
- Audit-ready report history
- Alert-driven operational visibility
- A controlled foundation for future optimization workflows

## Architecture

AWS FinOps Control Tower
|
|-- Terraform Foundation
|   |-- S3 Reports Bucket
|   |-- SNS Alerts
|   |-- IAM Execution Role
|   |-- CloudWatch Logs
|
|-- Execution Layer
|   |-- Lambda Runner
|   |-- EventBridge Schedule
|
|-- Real FinOps Discovery Engine
    |-- EC2 Inventory
    |-- EBS Inventory
    |-- Elastic IP Inventory
    |-- CloudWatch CPU Analysis
    |-- Finding Classification
    |-- S3 JSON Reports
    |-- SNS Executive Alerts

## Interview Positioning

In Phase 3, I integrated a real non-destructive FinOps discovery engine into AWS Lambda.

The engine scans EC2, EBS, and Elastic IP resources, correlates EC2 instances with CloudWatch CPU utilization, classifies findings by severity and category, stores audit-ready JSON reports in S3, and sends executive summaries through SNS.

The system provides actionable FinOps visibility without performing destructive actions.

## Next Phase

Phase 4 should introduce cost impact estimation.

The next objective is to estimate monthly financial exposure for:

- Idle EC2 instances
- Underutilized EC2 instances
- Unattached EBS volumes
- gp2 to gp3 migration candidates
- Unused Elastic IPs

This will transform findings from technical recommendations into financial decisions.
