# EC2 Runner + Cron + IAM Role

## Objetivo

Automatizar la ejecución diaria del sistema FinOps:

```text
EC2 (FinOps Runner)
   ↓
cron diario
   ↓
script FinOps
   ↓
S3 (reportes + logs)
   ↓
SNS (alertas)
```

---

## 1. Crear IAM Trust Policy

```powershell
New-Item iam\ec2-trust-policy.json
```

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "ec2.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

---

## 2. Crear IAM Role

```powershell
aws iam create-role `
  --role-name FinOpsControlTowerRunnerRole `
  --assume-role-policy-document file://iam/ec2-trust-policy.json `
  --profile sentinel
```

---

## 3. Crear Policy FinOps

Archivo ya creado previamente:

```text
iam\finops-control-tower-policy.json
```

Crear en AWS:

```powershell
aws iam create-policy `
  --policy-name FinOpsControlTowerRunnerPolicy `
  --policy-document file://iam/finops-control-tower-policy.json `
  --profile sentinel
```

---

## 4. Adjuntar Policy al Role

Reemplaza `<ACCOUNT_ID>`:

```powershell
aws iam attach-role-policy `
  --role-name FinOpsControlTowerRunnerRole `
  --policy-arn arn:aws:iam::<ACCOUNT_ID>:policy/FinOpsControlTowerRunnerPolicy `
  --profile sentinel
```

---

## 5. Crear Instance Profile

```powershell
aws iam create-instance-profile `
  --instance-profile-name FinOpsControlTowerRunnerProfile `
  --profile sentinel
```

```powershell
aws iam add-role-to-instance-profile `
  --instance-profile-name FinOpsControlTowerRunnerProfile `
  --role-name FinOpsControlTowerRunnerRole `
  --profile sentinel
```

---

## 6. Crear EC2 Runner

Configuración recomendada:

```text
AMI: Amazon Linux 2023
Instance Type: t3.micro
Storage: 8–20 GB gp3
IAM Role: FinOpsControlTowerRunnerRole
Security: sin inbound público (usar SSM)
```

---

## 7. Preparar EC2

Entrar por SSM:

```bash
sudo dnf update -y
sudo dnf install -y git python3 python3-pip cronie
sudo systemctl enable crond
sudo systemctl start crond
```

---

## 8. Clonar proyecto

```bash
cd /opt
sudo git clone https://github.com/ferkuellar/finops-control-tower.git
sudo chown -R ec2-user:ec2-user /opt/finops-control-tower
cd /opt/finops-control-tower
```

---

## 9. Crear entorno Python

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Validar IAM Role:

```bash
aws sts get-caller-identity
```

---

## 10. Script de ejecución diaria

```bash
nano /opt/finops-control-tower/scripts/run_finops_daily.sh
```

```bash
#!/bin/bash

set -e

PROJECT_DIR="/opt/finops-control-tower"
BUCKET="finops-control-tower-reports-ferkuellar"
SNS_TOPIC_ARN="arn:aws:sns:us-east-1:<ACCOUNT_ID>:finops-control-tower-alerts"
REGION="us-east-1"
ALERT_THRESHOLD="100"

DATE=$(date +"%Y-%m-%d_%H-%M-%S")
LOG_DIR="$PROJECT_DIR/logs"
LOG_FILE="$LOG_DIR/finops_scan_$DATE.log"

mkdir -p "$LOG_DIR"

cd "$PROJECT_DIR"

source .venv/bin/activate

echo "Starting FinOps scan: $DATE" | tee "$LOG_FILE"

python3 src/main.py scan \
  --all-regions \
  --upload-s3 \
  --report-bucket "$BUCKET" \
  --sns-topic-arn "$SNS_TOPIC_ARN" \
  --alert-threshold "$ALERT_THRESHOLD" \
  2>&1 | tee -a "$LOG_FILE"

echo "Uploading log to S3..." | tee -a "$LOG_FILE"

aws s3 cp "$LOG_FILE" "s3://$BUCKET/logs/finops_scan_$DATE.log" --region "$REGION" | tee -a "$LOG_FILE"

echo "FinOps scan completed: $DATE" | tee -a "$LOG_FILE"
```

Permisos:

```bash
chmod +x /opt/finops-control-tower/scripts/run_finops_daily.sh
```

---

## 11. Prueba manual

```bash
/opt/finops-control-tower/scripts/run_finops_daily.sh
```

---

## 12. Programar cron

```bash
crontab -e
```

```bash
0 7 * * * /opt/finops-control-tower/scripts/run_finops_daily.sh
```

Verificar:

```bash
crontab -l
```

---

## 13. Validar logs

```bash
ls -lah /opt/finops-control-tower/logs
tail -100 /opt/finops-control-tower/logs/finops_scan_*.log
```

---

## 14. Validar S3

```bash
aws s3 ls s3://finops-control-tower-reports-ferkuellar/finops-control-tower/ --recursive
aws s3 ls s3://finops-control-tower-reports-ferkuellar/logs/ --recursive
```

---

## Resultado

Sistema FinOps automatizado:

```text
✔ Escaneo diario automático
✔ Reportes JSON / CSV / Markdown / PDF
✔ Almacenamiento en S3
✔ Logs auditables
✔ Alertas por SNS/email
✔ Sin credenciales hardcodeadas (IAM Role)
```

---
