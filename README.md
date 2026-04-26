# AWS FinOps Control Tower

Production-oriented FinOps CLI tool designed to inventory, analyze, and optimize AWS cloud spend across multiple regions.

This project correlates:

- AWS resource inventory
- CloudWatch utilization metrics
- Cost Explorer spend data
- AWS Price List API pricing
- FinOps decision rules
- Executive reporting

The goal is simple:

> Identify what is running, what it costs, whether it is being used, who owns it, and what action should be taken.

---

## Problem Statement

Cloud environments drift over time.

Common issues:

- Orphaned infrastructure
- Idle EC2 instances
- Unattached EBS volumes
- Unused Elastic IPs
- Expensive NAT Gateways
- Missing S3 lifecycle policies
- Overprovisioned workloads
- Weak tagging discipline

This produces cloud spend without clear ownership or business justification.

---

## Objective

Build a repeatable FinOps assessment pipeline that can:

- Scan AWS accounts across regions
- Detect cost leaks
- Classify findings by risk
- Estimate monthly savings exposure
- Generate executive and technical reports

---

## Architecture

```text
AWS Account
   |
   |-- EC2 / EBS
   |-- RDS
   |-- S3
   |-- Lambda
   |-- Elastic IP
   |-- NAT Gateway
   |-- Load Balancer
   |
   v
Python FinOps CLI
   |
   |-- Inventory Collection
   |-- CloudWatch Metrics
   |-- Cost Explorer
   |-- AWS Price List API
   |-- Recommendation Engine
   |
   v
Reports
   |
   |-- Executive Markdown Report
   |-- JSON Dataset
   |-- CSV Exports
```

---

## FinOps Model

| Layer       | Purpose                       |
|-------------|-------------------------------|
| Inventory   | Discover AWS resources        |
| Utilization | Measure real usage            |
| Cost        | Understand spend and exposure |
| Decision    | Classify resources            |
| Reporting   | Produce actionable output     |

---

## Services Covered

| AWS Area   | Resources                               |
|------------|-----------------------------------------|
| Compute    | EC2, Lambda                             |
| Storage    | EBS, S3                                 |
| Database   | RDS                                     |
| Networking | Elastic IP, NAT Gateway, Load Balancers |
| Billing    | Cost Explorer                           |
| Pricing    | AWS Price List API                      |
| Monitoring | CloudWatch                              |

---

## Recommendations Generated

| Finding                    | Recommendation             |
|----------------------------|----------------------------|
| EC2 CPU < 5%               | Stop / Terminate candidate |
| EC2 CPU 5–20%              | Rightsizing candidate      |
| Missing tags               | Fix tagging                |
| Unattached EBS             | Delete candidate           |
| GP2 volume                 | Migrate to GP3             |
| Unused Elastic IP          | Release                    |
| S3 without lifecycle       | Add lifecycle policy       |
| RDS Multi-AZ in dev        | Review configuration       |
| NAT Gateway active         | Validate traffic           |
| Lambda high memory/timeout | Tune configuration         |

---

## Project Structure

```text
finops-control-tower/
│
├── src/
│   ├── main.py
│   ├── aws_clients.py
│   ├── ui.py
│   ├── regions.py
│   ├── costs.py
│   ├── metrics.py
│   ├── inventory.py
│   ├── recommendations.py
│   ├── rds.py
│   ├── s3_scan.py
│   ├── lambda_scan.py
│   ├── networking.py
│   ├── executive_summary.py
│   ├── savings.py
│   ├── reporting.py
│   └── consolidated_report.py
│
├── reports/
│   ├── finops_executive_report_<timestamp>.md
│   ├── finops_report_<timestamp>.json
│   ├── ec2_inventory_<timestamp>.csv
│   └── ebs_inventory_<timestamp>.csv
│
├── docs/
│   └── evidence/
│
├── config/
├── scripts/
├── iam/
├── requirements.txt
├── .gitignore
└── README.md
```

---

## Requirements

- Python 3.10+
- AWS CLI configured
- AWS IAM permissions for read-only FinOps discovery
- Cost Explorer enabled
- CloudWatch metrics available

---

## Installation

```powershell
cd D:\projects
git clone https://github.com/ferkuellar/finops-control-tower.git
cd finops-control-tower

python -m venv .venv
.\.venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

---

## AWS CLI Profile

List profiles:

```powershell
aws configure list-profiles
```

Validate identity:

```powershell
aws sts get-caller-identity --profile sentinel
```

Expected output:

```json
{
  "UserId": "AIDAxxxxxxxxxxxxx",
  "Account": "123456789012",
  "Arn": "arn:aws:iam::123456789012:user/finops-user"
}
```

---

## Usage

Scan one region:

```powershell
python .\src\main.py scan --profile sentinel --region us-east-1
```

Scan all enabled regions:

```powershell
python .\src\main.py scan --profile sentinel --all-regions
```

Disable exports:

```powershell
python .\src\main.py scan --profile sentinel --region us-east-1 --no-export
```

---

## Output

The CLI generates:

```text
reports/
  finops_executive_report_<timestamp>.md
  finops_report_<timestamp>.json
  ec2_inventory_<timestamp>.csv
  ebs_inventory_<timestamp>.csv
```

---

## Example Executive Output

```text
Executive FinOps Summary

Area          Finding                              Count   Action
EC2           Low CPU / terminate-stop candidates  2       Validate owner, then stop/terminate
EC2           Rightsizing candidates               3       Resize after workload validation
EBS           Unattached volumes                   2       Snapshot if needed, then delete
Elastic IP    Unused public IPs                    1       Release unused Elastic IPs
S3            Buckets without lifecycle policy     2       Add lifecycle policy
RDS           Databases requiring review           1       Review Multi-AZ, storage, dev usage
NAT Gateway   NAT Gateways requiring validation    1       Validate traffic and architecture
Lambda        Functions requiring review           1       Tune memory and timeout
```

---

## Example Savings Output

```text
Estimated Monthly Savings / Cost Exposure

Resource      Region     ID                  Est. Monthly Cost USD    Pricing Source
EC2           us-east-1  i-abc123             $30.37                   AWS Price List API
EBS           us-east-1  vol-abc123           $8.00                    AWS Price List API
NAT Gateway   us-east-1  nat-abc123           $32.85 + traffic         AWS Price List API + CloudWatch

Estimated Monthly Savings / Cost Exposure: $71.22 USD
```

---

## Report Example

The Markdown executive report includes:

- Executive summary
- Top cost services
- Immediate action items
- Optimization opportunities
- Inventory totals
- Recommended execution plan
- Risk controls

---

## IAM Permissions

Recommended read-only policy actions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "FinOpsReadOnlyDiscovery",
      "Effect": "Allow",
      "Action": [
        "ec2:Describe*",
        "rds:Describe*",
        "rds:ListTagsForResource",
        "s3:ListAllMyBuckets",
        "s3:GetBucketLifecycleConfiguration",
        "lambda:ListFunctions",
        "elasticloadbalancing:Describe*",
        "cloudwatch:GetMetricStatistics",
        "ce:GetCostAndUsage",
        "pricing:GetProducts"
      ],
      "Resource": "*"
    }
  ]
}
```

---

## Operating Model

This tool is decision support, not auto-remediation.

Before stopping, deleting, resizing, or modifying resources:

- Validate ownership
- Confirm business criticality
- Verify backups
- Confirm rollback plan
- Confirm production impact
- Document approval

---

## FinOps Maturity Impact

| Maturity Stage | Capability                          |
|----------------|-------------------------------------|
| Initial        | Manual cost inspection              |
| Inform         | Cost and inventory visibility       |
| Optimize       | Actionable recommendations          |
| Operate        | Repeatable reporting and governance |

This tool helps move from manual inspection to repeatable FinOps operations.

---

## Roadmap

Planned improvements:

- AWS Compute Optimizer integration
- AWS Trusted Advisor integration
- NAT Gateway traffic-based cost calculation
- S3 size and storage class analysis
- SNS/email alerting
- S3 archival of reports
- EC2 runner automation
- GitHub Actions validation
- Dashboard layer

---

## Author

Fernando Cuellar  
Cloud / DevOps / FinOps Engineer

---

# 2. Crear `docs/evidence/README.md`

Crea la carpeta y el archivo de evidencia:

```powershell
New-Item -ItemType Directory -Force docs\evidence
New-Item -ItemType File -Force docs\evidence\README.md
```

Luego agrega el siguiente contenido en `docs/evidence/README.md`:

---

# Evidence

This folder contains CLI outputs, screenshots, and generated reports used to validate the AWS FinOps Control Tower project.

---

## Suggested Evidence Files

```text
01-aws-identity.txt
02-cost-overview.txt
03-ec2-ebs-inventory.txt
04-extended-inventory.txt
05-recommendations.txt
06-executive-summary.txt
07-savings-estimation.txt
08-generated-reports.txt
```

---

## Recommended Capture Commands

Capture AWS identity:

```powershell
aws sts get-caller-identity --profile sentinel *> docs\evidence\01-aws-identity.txt
```

Capture one-region execution:

```powershell
python .\src\main.py scan --profile sentinel --region us-east-1 *> docs\evidence\scan-output.txt
```

Capture multi-region execution:

```powershell
python .\src\main.py scan --profile sentinel --all-regions *> docs\evidence\scan-output-all-regions.txt
```

---

## Evidence Rules

Before adding evidence to the repository:

- Do not commit secrets.
- Do not commit access keys.
- Do not commit account-sensitive outputs unless sanitized.
- Review every file before pushing to GitHub.
- Keep evidence concise, readable, and useful for interviews or technical review.

---

# 3. Crear comando de evidencia

Ejecuta un escaneo por región:

```powershell
python .\src\main.py scan --profile sentinel --region us-east-1 *> docs\evidence\scan-output.txt
```

O ejecuta un escaneo multi-región:

```powershell
python .\src\main.py scan --profile sentinel --all-regions *> docs\evidence\scan-output-all-regions.txt
```

---

# 4. Validar reportes

```powershell
dir reports
dir docs\evidence
```

---

# 5. Guardar en Git

```powershell
git status
git add .
git commit -m "Add CTO-level README and evidence documentation"
```

---

# 6. Crear repo remoto en GitHub

Nombre sugerido:

```text
finops-control-tower
```

Descripción sugerida:

```text
AWS FinOps CLI for multi-region inventory, cost visibility, utilization analysis, savings estimation, and executive reporting.
```

---

# 7. Conectar repo local con GitHub

Reemplaza la URL por la tuya:

```powershell
git branch -M main
git remote add origin https://github.com/ferkuellar/finops-control-tower.git
git push -u origin main
```

Si ya existe `origin`:

```powershell
git remote set-url origin https://github.com/ferkuellar/finops-control-tower.git
git push -u origin main
```

---

# 8. Comando final demo

Este es el comando que usarías en demo o entrevista:

```powershell
python .\src\main.py scan --profile sentinel --all-regions
```

Frase para explicar:

```text
This command performs a multi-region FinOps scan, correlates inventory, utilization, cost data and pricing exposure, generates recommendations, and produces executive and operational reports.
```

---
