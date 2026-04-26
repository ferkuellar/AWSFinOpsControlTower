from datetime import datetime
from pathlib import Path

REPORT_DIR = Path("reports")


def _contains(item: dict, keyword: str):
    return keyword.upper() in str(item.get("recommendation", "")).upper()


def generate_consolidated_markdown(report: dict, total_savings: float = 0.0):
    REPORT_DIR.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = REPORT_DIR / f"finops_executive_report_{timestamp}.md"

    cost_summary = report.get("cost_summary", {})

    ec2 = report.get("ec2_instances", [])
    ebs = report.get("ebs_volumes", [])
    rds = report.get("rds_instances", [])
    eips = report.get("elastic_ips", [])
    nat = report.get("nat_gateways", [])
    lbs = report.get("load_balancers", [])
    lambdas = report.get("lambda_functions", [])
    s3 = report.get("s3_buckets", [])

    total_resources = (
        len(ec2)
        + len(ebs)
        + len(rds)
        + len(eips)
        + len(nat)
        + len(lbs)
        + len(lambdas)
        + len(s3)
    )

    high_risk_ec2 = [
        i for i in ec2
        if i.get("risk") == "HIGH"
    ]

    rightsizing_ec2 = [
        i for i in ec2
        if _contains(i, "RIGHTSIZE")
    ]

    unattached_ebs = [
        v for v in ebs
        if _contains(v, "DELETE")
    ]

    gp2_volumes = [
        v for v in ebs
        if _contains(v, "GP3")
    ]

    unused_eips = [
        ip for ip in eips
        if _contains(ip, "RELEASE")
    ]

    s3_without_lifecycle = [
        b for b in s3
        if _contains(b, "LIFECYCLE")
    ]

    rds_review = [
        db for db in rds
        if _contains(db, "REVIEW")
    ]

    nat_review = [
        n for n in nat
        if _contains(n, "VERIFY") or _contains(n, "REVIEW")
    ]

    lambda_review = [
        f for f in lambdas
        if _contains(f, "REVIEW")
    ]

    with open(file_path, "w", encoding="utf-8") as f:
        f.write("# AWS FinOps Executive Assessment Report\n\n")
        f.write("---\n\n")

        f.write("## 1. Executive Summary\n\n")
        f.write(f"- AWS profile analyzed: `{report.get('profile')}`\n")
        f.write(f"- Regions analyzed: `{', '.join(report.get('regions', []))}`\n")
        f.write(f"- Cost period: `{cost_summary.get('start', 'N/A')} to {cost_summary.get('end', 'N/A')}`\n")
        f.write(f"- Total monthly spend detected: **${cost_summary.get('total', 0):,.2f} USD**\n")
        f.write(f"- Total resources inventoried: **{total_resources}**\n")
        f.write(f"- High-risk EC2 findings: **{len(high_risk_ec2)}**\n")
        f.write(f"- EC2 rightsizing candidates: **{len(rightsizing_ec2)}**\n")
        f.write(f"- Unattached EBS volumes: **{len(unattached_ebs)}**\n")
        f.write(f"- Unused Elastic IPs: **{len(unused_eips)}**\n")
        f.write(f"- Estimated monthly savings / exposure: **${total_savings:,.2f} USD**\n\n")

        f.write("---\n\n")

        f.write("## 2. FinOps Position\n\n")
        f.write(
            "The AWS environment was assessed using a FinOps-oriented approach focused on "
            "resource ownership, utilization, pricing exposure, and operational risk. "
            "The priority is to eliminate orphaned resources first, optimize underutilized "
            "compute and storage second, and then implement governance controls to prevent "
            "future cost drift.\n\n"
        )

        f.write("---\n\n")

        f.write("## 3. Top Cost Services\n\n")
        services = cost_summary.get("services", [])

        if services:
            f.write("| Service | Cost USD |\n")
            f.write("|---|---:|\n")
            for service in services[:10]:
                f.write(
                    f"| {service.get('service')} | "
                    f"${service.get('amount', 0):,.2f} |\n"
                )
        else:
            f.write("No Cost Explorer data available.\n")

        f.write("\n---\n\n")

        f.write("## 4. Immediate Action Items\n\n")

        f.write("### EC2 High-Risk Instances\n\n")
        if high_risk_ec2:
            f.write("| Region | Instance ID | Name | Type | State | Avg CPU 7d | Risk | Recommendation |\n")
            f.write("|---|---|---|---|---|---:|---|---|\n")
            for i in high_risk_ec2:
                f.write(
                    f"| {i.get('region')} | {i.get('id')} | {i.get('name')} | "
                    f"{i.get('type')} | {i.get('state')} | {i.get('avg_cpu_7d')} | "
                    f"{i.get('risk')} | {i.get('recommendation')} |\n"
                )
        else:
            f.write("No high-risk EC2 findings detected.\n")

        f.write("\n")

        f.write("### Unattached EBS Volumes\n\n")
        if unattached_ebs:
            f.write("| Region | Volume ID | Type | Size GiB | State | Recommendation |\n")
            f.write("|---|---|---|---:|---|---|\n")
            for v in unattached_ebs:
                f.write(
                    f"| {v.get('region')} | {v.get('id')} | {v.get('type')} | "
                    f"{v.get('size')} | {v.get('state')} | {v.get('recommendation')} |\n"
                )
        else:
            f.write("No unattached EBS volumes detected.\n")

        f.write("\n")

        f.write("### Unused Elastic IPs\n\n")
        if unused_eips:
            f.write("| Region | Public IP | Allocation ID | Recommendation |\n")
            f.write("|---|---|---|---|\n")
            for ip in unused_eips:
                f.write(
                    f"| {ip.get('region')} | {ip.get('public_ip')} | "
                    f"{ip.get('allocation_id')} | {ip.get('recommendation')} |\n"
                )
        else:
            f.write("No unused Elastic IPs detected.\n")

        f.write("\n---\n\n")

        f.write("## 5. Optimization Opportunities\n\n")

        f.write("### EC2 Rightsizing Candidates\n\n")
        if rightsizing_ec2:
            f.write("| Region | Instance ID | Name | Type | Avg CPU 7d | Recommendation |\n")
            f.write("|---|---|---|---|---:|---|\n")
            for i in rightsizing_ec2:
                f.write(
                    f"| {i.get('region')} | {i.get('id')} | {i.get('name')} | "
                    f"{i.get('type')} | {i.get('avg_cpu_7d')} | {i.get('recommendation')} |\n"
                )
        else:
            f.write("No EC2 rightsizing candidates detected.\n")

        f.write("\n")

        f.write("### EBS GP2 to GP3 Migration Candidates\n\n")
        if gp2_volumes:
            f.write("| Region | Volume ID | Size GiB | Recommendation |\n")
            f.write("|---|---|---:|---|\n")
            for v in gp2_volumes:
                f.write(
                    f"| {v.get('region')} | {v.get('id')} | "
                    f"{v.get('size')} | {v.get('recommendation')} |\n"
                )
        else:
            f.write("No GP2 to GP3 migration candidates detected.\n")

        f.write("\n")

        f.write("### S3 Buckets Without Lifecycle Policy\n\n")
        if s3_without_lifecycle:
            f.write("| Bucket | Recommendation |\n")
            f.write("|---|---|\n")
            for b in s3_without_lifecycle:
                f.write(
                    f"| {b.get('bucket')} | {b.get('recommendation')} |\n"
                )
        else:
            f.write("All reviewed buckets have lifecycle policies or no S3 buckets were detected.\n")

        f.write("\n")

        f.write("### RDS Review Items\n\n")
        if rds_review:
            f.write("| Region | DB ID | Class | Engine | Multi-AZ | Storage GB | Status | Recommendation |\n")
            f.write("|---|---|---|---|---|---:|---|---|\n")
            for db in rds_review:
                f.write(
                    f"| {db.get('region')} | {db.get('id')} | {db.get('class')} | "
                    f"{db.get('engine')} | {db.get('multi_az')} | {db.get('storage')} | "
                    f"{db.get('status')} | {db.get('recommendation')} |\n"
                )
        else:
            f.write("No RDS review items detected.\n")

        f.write("\n")

        f.write("### NAT Gateway Review Items\n\n")
        if nat_review:
            f.write("| Region | NAT Gateway ID | State | VPC | Recommendation |\n")
            f.write("|---|---|---|---|---|\n")
            for n in nat_review:
                f.write(
                    f"| {n.get('region')} | {n.get('id')} | "
                    f"{n.get('state')} | {n.get('vpc_id')} | {n.get('recommendation')} |\n"
                )
        else:
            f.write("No NAT Gateway review items detected.\n")

        f.write("\n")

        f.write("### Lambda Review Items\n\n")
        if lambda_review:
            f.write("| Region | Function | Runtime | Memory MB | Timeout Sec | Recommendation |\n")
            f.write("|---|---|---|---:|---:|---|\n")
            for fn in lambda_review:
                f.write(
                    f"| {fn.get('region')} | {fn.get('name')} | {fn.get('runtime')} | "
                    f"{fn.get('memory')} | {fn.get('timeout')} | {fn.get('recommendation')} |\n"
                )
        else:
            f.write("No Lambda tuning candidates detected.\n")

        f.write("\n---\n\n")

        f.write("## 6. Inventory Totals\n\n")
        f.write("| Resource Type | Count |\n")
        f.write("|---|---:|\n")
        f.write(f"| EC2 Instances | {len(ec2)} |\n")
        f.write(f"| EBS Volumes | {len(ebs)} |\n")
        f.write(f"| RDS Instances | {len(rds)} |\n")
        f.write(f"| S3 Buckets | {len(s3)} |\n")
        f.write(f"| Lambda Functions | {len(lambdas)} |\n")
        f.write(f"| Elastic IPs | {len(eips)} |\n")
        f.write(f"| NAT Gateways | {len(nat)} |\n")
        f.write(f"| Load Balancers | {len(lbs)} |\n\n")

        f.write("---\n\n")

        f.write("## 7. Recommended Execution Plan\n\n")
        f.write("### Phase 1 — Immediate Cleanup\n\n")
        f.write("- Validate ownership and business criticality.\n")
        f.write("- Snapshot unattached EBS volumes only if retention is required.\n")
        f.write("- Release unused Elastic IPs.\n")
        f.write("- Stop or terminate confirmed idle EC2 instances.\n\n")

        f.write("### Phase 2 — Optimization\n\n")
        f.write("- Resize EC2 instances with sustained low utilization.\n")
        f.write("- Migrate GP2 volumes to GP3 where applicable.\n")
        f.write("- Add lifecycle policies to S3 buckets.\n")
        f.write("- Review RDS dev/test configurations, Multi-AZ usage, and allocated storage.\n")
        f.write("- Validate NAT Gateway traffic before making architecture changes.\n\n")

        f.write("### Phase 3 — Governance\n\n")
        f.write("- Enforce required tags: Owner, Environment, Application, CostCenter.\n")
        f.write("- Configure AWS Budgets by account and workload.\n")
        f.write("- Add recurring weekly FinOps scans.\n")
        f.write("- Publish monthly executive cost reports.\n\n")

        f.write("---\n\n")

        f.write("## 8. Risk Control\n\n")
        f.write(
            "No production resource should be deleted or resized without validating ownership, "
            "business criticality, backup status, and rollback path. FinOps is controlled cost "
            "governance, not random cleanup.\n"
        )

    return file_path