# Phase 4 - Cost Impact Estimation

## Objective

This phase extends the AWS FinOps Control Tower from technical finding generation into financial impact estimation.

The system now estimates monthly and annual financial exposure for:

- Idle EC2 instances
- Underutilized EC2 instances
- Unattached EBS volumes
- gp2 to gp3 migration candidates
- Unused Elastic IPs

## Execution Model

EventBridge
   |
   v
Lambda FinOps Runner
   |
   |-- Scan EC2, EBS, and Elastic IP resources
   |-- Analyze CloudWatch CPU utilization
   |-- Generate FinOps findings
   |-- Estimate monthly savings
   |-- Estimate annual savings
   |-- Store JSON report in S3
   |-- Send SNS executive summary

## Cost Estimation Scope

| Resource | Financial Logic |
|---|---|
| Idle EC2 | Estimated full monthly compute waste |
| Underutilized EC2 | Estimated rightsizing opportunity |
| Unattached EBS | Estimated monthly storage waste |
| gp2 EBS | Estimated gp2 to gp3 migration savings |
| Unused Elastic IP | Estimated monthly public IPv4 waste |

## Pricing Assumptions

This phase uses configurable assumptions instead of hard-coded claims.

Current variables:

- monthly_hours
- default_ec2_hourly_rate
- rightsize_savings_factor
- ebs_gp2_gb_month_rate
- ebs_gp3_gb_month_rate
- public_ipv4_hourly_rate

These values are defined in Terraform and injected into Lambda as environment variables.

## Safety Model

This phase is non-destructive.

The system does not:

- Stop EC2 instances
- Terminate EC2 instances
- Delete EBS volumes
- Release Elastic IPs
- Modify infrastructure
- Apply recommendations automatically

All savings are estimates only.

Execution requires:

1. Ownership validation
2. Environment classification
3. Backup verification
4. Business impact review
5. Approval
6. Rollback planning

## Report Location

Reports are stored in S3 using the following prefix:

reports/finops-cost-impact/

## Evidence

Validation evidence is stored under:

docs/evidence/phase-4/

Expected evidence files:

- terraform-validate.txt
- terraform-outputs.txt
- phase-4-response.json
- s3-finops-cost-impact-reports.txt
- reports/

## Business Value

This phase transforms FinOps findings from technical observations into financial decision points.

It provides:

- Estimated monthly savings
- Estimated annual savings
- Severity-based prioritization
- Financial exposure visibility
- Executive-ready reporting
- Audit-ready evidence trail

## Interview Positioning

In Phase 4, I extended the AWS FinOps Control Tower with cost impact estimation.

The system now correlates technical findings with configurable financial assumptions to estimate monthly and annual savings for idle compute, underutilized compute, orphaned storage, gp2-to-gp3 migration candidates, and unused Elastic IPs.

The design remains non-destructive and audit-focused. It provides financial decision support without automatically modifying infrastructure.

## Next Phase

Phase 5 should introduce CSV and Markdown executive report generation.

The next objective is to produce human-readable reports for:

- Engineering teams
- FinOps stakeholders
- Finance leadership
- Executive review
