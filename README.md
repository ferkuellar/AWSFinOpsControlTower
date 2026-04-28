
# AWS FinOps Control Tower

### Terraform-Provisioned FinOps Operating Model for AWS Cost Visibility, Governance, and Financial Decision Support

---

## 1. Executive Overview

**AWS FinOps Control Tower** is a production-oriented FinOps framework that transforms AWS infrastructure signals into **financial visibility, risk classification, and controlled optimization recommendations**.

The project combines two layers:

1. **Terraform Control Plane**  
   Provisions the AWS foundation required to operate the FinOps platform: IAM, S3, SNS, Lambda, EventBridge, and CloudWatch Logs.

2. **Python FinOps Engine**  
   Performs non-destructive discovery, utilization analysis, finding classification, and cost impact estimation for AWS resources.

This is not just a cost optimization script.

It is a **FinOps decision framework implemented as code**.

---

## 2. Problem Statement

In high-growth AWS environments, cloud cost increases are rarely linear. They are usually caused by a mix of technical waste, weak ownership, poor tagging discipline, and delayed financial governance.

Common drivers include:

- Idle EC2 instances
- Underutilized compute
- Orphaned EBS volumes
- Legacy gp2 storage
- Unused Elastic IPs
- Missing ownership metadata
- Lack of scheduled cost visibility
- Lack of audit-ready optimization evidence

The real problem is not cloud cost by itself.

The real problem is the absence of a repeatable operating model that connects:

```text
Inventory + Utilization + Cost + Ownership + Decision
````

---

## 3. Solution Positioning

This project implements a controlled FinOps pipeline that discovers AWS resources, evaluates utilization, estimates financial impact, stores audit-ready reports, and notifies stakeholders.

The system is intentionally **non-destructive**.

It does not delete, stop, resize, or release infrastructure automatically. It generates recommendations that require business validation and approval.

---

## 4. Current Architecture

```text
AWS Account
   |
   |-- EC2 Instances
   |-- EBS Volumes
   |-- Elastic IPs
   |-- CloudWatch Metrics
   |
   v
Terraform-Provisioned Control Plane
   |
   |-- IAM Execution Role
   |-- S3 Reports Bucket
   |-- SNS Alert Topic
   |-- Lambda Runner
   |-- EventBridge Schedule
   |-- CloudWatch Logs
   |
   v
Python FinOps Engine
   |
   |-- Inventory Discovery
   |-- CloudWatch CPU Analysis
   |-- Finding Classification
   |-- Cost Impact Estimation
   |
   v
Reporting and Alerting Layer
   |
   |-- JSON Reports in S3
   |-- SNS Executive Notifications
   |-- CloudWatch Execution Logs
   |-- Evidence under docs/evidence/
```

---

## 5. Repository Structure

```text
AWSFinOpsControlTower/
|
|-- terraform/
|   |-- providers.tf
|   |-- variables.tf
|   |-- terraform.tfvars
|   |-- s3.tf
|   |-- sns.tf
|   |-- iam.tf
|   |-- logs.tf
|   |-- lambda.tf
|   |-- eventbridge.tf
|   |-- outputs.tf
|   |
|   |-- lambda/
|       |-- finops_runner.py
|
|-- docs/
|   |-- phase-2-execution-layer.md
|   |-- phase-3-real-finops-discovery.md
|   |-- phase-4-cost-impact-estimation.md
|   |
|   |-- evidence/
|       |-- phase-1/
|       |-- phase-2/
|       |-- phase-3/
|       |-- phase-4/
|
|-- reports/
|-- src/
|-- README.md
```

---

## 6. Terraform-Provisioned AWS Components

| Component        | Purpose                                                            |
| ---------------- | ------------------------------------------------------------------ |
| S3 Bucket        | Stores FinOps reports and audit evidence                           |
| SNS Topic        | Sends executive and operational alerts                             |
| IAM Role         | Provides controlled permissions for Lambda execution               |
| Lambda Function  | Runs the FinOps discovery and cost impact engine                   |
| EventBridge Rule | Executes the scanner on a schedule                                 |
| CloudWatch Logs  | Captures execution logs and troubleshooting data                   |
| Default Tags     | Enforces ownership, environment, project, and cost center metadata |

---

## 7. FinOps Engine Capabilities

The current Lambda-based FinOps engine analyzes:

* EC2 instances
* EBS volumes
* Elastic IPs
* CloudWatch CPU utilization metrics

It generates findings for:

| Resource | Detection Rule                      | Severity | Recommendation                                         |
| -------- | ----------------------------------- | -------- | ------------------------------------------------------ |
| EC2      | Running with CPU below 5%           | High     | Review, stop, terminate, or rightsize after validation |
| EC2      | Running with CPU between 5% and 20% | Medium   | Evaluate rightsizing                                   |
| EC2      | Stopped instance                    | Medium   | Review attached EBS and ownership                      |
| EBS      | Available or unattached volume      | High     | Snapshot if required, then delete after approval       |
| EBS      | gp2 volume                          | Medium   | Evaluate migration to gp3                              |
| EBS      | Unencrypted volume                  | Medium   | Review encryption requirements                         |
| EIP      | No association                      | High     | Release after ownership validation                     |

---

## 8. Cost Impact Estimation

Phase 4 extends the system from technical recommendations into financial decision support.

The engine estimates monthly and annual savings for:

* Idle EC2 instances
* Underutilized EC2 instances
* Unattached EBS volumes
* gp2 to gp3 migration candidates
* Unused Elastic IPs

Pricing is intentionally configurable through Terraform variables and Lambda environment variables.

Current assumptions include:

| Variable                 | Purpose                                                      |
| ------------------------ | ------------------------------------------------------------ |
| monthly_hours            | Standard monthly hour baseline                               |
| default_ec2_hourly_rate  | Placeholder EC2 hourly rate until Price List API integration |
| rightsize_savings_factor | Estimated savings percentage for rightsizing                 |
| ebs_gp2_gb_month_rate    | Estimated gp2 GB-month rate                                  |
| ebs_gp3_gb_month_rate    | Estimated gp3 GB-month rate                                  |
| public_ipv4_hourly_rate  | Estimated public IPv4 hourly rate                            |

This avoids overstating savings while still creating a clear financial prioritization model.

---

## 9. Execution Model

```text
EventBridge Schedule
   |
   v
Lambda FinOps Runner
   |
   |-- Scan EC2 inventory
   |-- Pull CloudWatch CPU metrics
   |-- Scan EBS volumes
   |-- Scan Elastic IPs
   |-- Generate findings
   |-- Estimate monthly and annual savings
   |-- Store JSON report in S3
   |-- Publish SNS alert
   v
Audit Trail and Executive Visibility
```

---

## 10. Report Locations

Reports are stored in S3 using prefixes such as:

```text
reports/execution-validation/
reports/finops-discovery/
reports/finops-cost-impact/
```

Local validation evidence is stored under:

```text
docs/evidence/phase-1/
docs/evidence/phase-2/
docs/evidence/phase-3/
docs/evidence/phase-4/
```

---

## 11. Deployment

From the Terraform directory:

```powershell
cd terraform
terraform init
terraform fmt
terraform validate
terraform plan -out=tfplan
terraform apply tfplan
```

Manual Lambda execution:

```powershell
aws lambda invoke `
  --function-name aws-finops-control-tower-dev-runner `
  --profile finops-lab `
  --region us-east-1 `
  phase-4-response.json
```

List generated cost impact reports:

```powershell
$bucket = terraform output -raw finops_reports_bucket_name

aws s3 ls s3://$bucket/reports/finops-cost-impact/ `
  --recursive `
  --profile finops-lab `
  --region us-east-1
```

Download generated reports:

```powershell
$bucket = terraform output -raw finops_reports_bucket_name

New-Item -ItemType Directory -Force -Path phase-4-reports

aws s3 sync s3://$bucket/reports/finops-cost-impact/ `
  .\phase-4-reports `
  --exclude "*:*" `
  --profile finops-lab `
  --region us-east-1
```

Inspect latest report:

```powershell
$latestReport = Get-ChildItem .\phase-4-reports -Recurse -Filter *.json |
  Sort-Object LastWriteTime -Descending |
  Select-Object -First 1

$report = Get-Content $latestReport.FullName | ConvertFrom-Json

$report.summary

$report.findings |
  Select-Object `
    resource_type, `
    resource_id, `
    severity, `
    category, `
    @{Name="monthly_savings_usd";Expression={$_.cost_impact.estimated_monthly_savings}}, `
    recommendation |
  Format-Table -AutoSize
```

---

## 12. Governance and Safety Model

This system is deliberately non-destructive.

It does not:

* Stop EC2 instances
* Terminate EC2 instances
* Delete EBS volumes
* Release Elastic IPs
* Modify infrastructure automatically
* Apply recommendations without approval

Every optimization recommendation requires:

1. Ownership validation
2. Environment classification
3. Backup verification
4. Business impact analysis
5. Approval
6. Rollback planning

This is intentional.

The system prioritizes governance, auditability, and controlled execution over aggressive automation.

---

## 13. Project Phases

| Phase   | Capability                                               | Status      |
| ------- | -------------------------------------------------------- | ----------- |
| Phase 1 | Terraform Foundation: S3, SNS, IAM, CloudWatch Logs      | Implemented |
| Phase 2 | Lambda Execution Layer with EventBridge schedule         | Implemented |
| Phase 3 | Real FinOps discovery for EC2, EBS, EIP, and CPU metrics | Implemented |
| Phase 4 | Cost impact estimation for monthly and annual savings    | Implemented |
| Phase 5 | CSV and Markdown executive reporting                     | Planned     |
| Phase 6 | AWS Price List API and Cost Explorer enrichment          | Planned     |
| Phase 7 | Multi-account / AWS Organizations support                | Planned     |

---

## 14. Trade-offs

This project deliberately avoids:

* Automatic deletion of resources
* Blind rightsizing
* Unreviewed cost actions
* Black-box ML recommendations
* Overstated savings claims

It prioritizes:

* Deterministic logic
* Explainable findings
* Audit-ready reports
* Human approval
* Financial governance
* Repeatable execution through Terraform

---

## 15. Current Limitations

* EC2 pricing uses configurable assumptions instead of live AWS Price List API data
* CPU-based rightsizing is a proxy, not full workload profiling
* No AWS Compute Optimizer integration yet
* No multi-account aggregation yet
* NAT Gateway and S3 lifecycle cost analysis are not yet included
* Savings estimates are directional and require validation before action
* Existing S3 report keys with colon characters in timestamps may fail to download on Windows unless renamed or excluded

---

## 16. Business Impact

This project demonstrates how FinOps can be operationalized using cloud-native automation and Infrastructure as Code.

It provides:

* Reduced cloud waste visibility
* Cost accountability by resource
* Financial impact estimation
* Scheduled optimization reporting
* Audit-ready evidence
* Clear approval boundaries
* Better communication between engineering, finance, and leadership

---

## 17. Positioning

I designed and implemented an AWS FinOps Control Tower using Terraform, Lambda, EventBridge, S3, SNS, IAM, CloudWatch, and Python.

Terraform provisions the operating foundation, while the Python engine performs non-destructive discovery, utilization analysis, finding classification, and cost impact estimation.

The system scans EC2, EBS, and Elastic IP resources, correlates EC2 instances with CloudWatch CPU utilization, estimates monthly and annual savings, stores audit-ready JSON reports in S3, and sends executive summaries through SNS.

The design focuses on governance, auditability, and controlled execution rather than aggressive automation.

---

## 18. Final Statement

This is not a simple AWS cost script.

This is a Terraform-provisioned FinOps control plane with a Python-based decision engine that converts AWS infrastructure signals into financial visibility, risk classification, and controlled optimization recommendations.

```
```
