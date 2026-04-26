from datetime import datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)


REPORT_DIR = Path("reports")


def _contains(item: dict, keyword: str):
    return keyword.upper() in str(item.get("recommendation", "")).upper()


def _money(value):
    return f"${value:,.2f} USD"


def _footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.grey)
    canvas.drawString(
        0.7 * inch,
        0.45 * inch,
        "AWS FinOps Control Tower - CFO Executive Report"
    )
    canvas.drawRightString(
        7.8 * inch,
        0.45 * inch,
        f"Page {doc.page}"
    )
    canvas.restoreState()


def generate_cfo_pdf_report(report: dict, total_savings: float = 0.0):
    REPORT_DIR.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = REPORT_DIR / f"finops_cfo_report_{timestamp}.pdf"

    doc = SimpleDocTemplate(
        str(file_path),
        pagesize=letter,
        rightMargin=0.55 * inch,
        leftMargin=0.55 * inch,
        topMargin=0.55 * inch,
        bottomMargin=0.65 * inch,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "CFO_Title",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#1F2937"),
        spaceAfter=16,
    )

    section_style = ParagraphStyle(
        "Section",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#111827"),
        spaceBefore=14,
        spaceAfter=8,
    )

    normal_style = ParagraphStyle(
        "Normal",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        alignment=TA_LEFT,
        textColor=colors.HexColor("#374151"),
    )

    small_style = ParagraphStyle(
        "Small",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#4B5563"),
    )

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

    ec2_terminate = [i for i in ec2 if _contains(i, "TERMINATE")]
    ec2_rightsize = [i for i in ec2 if _contains(i, "RIGHTSIZE")]
    unattached_ebs = [v for v in ebs if _contains(v, "DELETE")]
    gp2_volumes = [v for v in ebs if _contains(v, "GP3")]
    unused_eips = [ip for ip in eips if _contains(ip, "RELEASE")]
    s3_lifecycle = [b for b in s3 if _contains(b, "LIFECYCLE")]
    rds_review = [db for db in rds if _contains(db, "REVIEW")]
    nat_review = [n for n in nat if _contains(n, "VERIFY") or _contains(n, "REVIEW")]
    lambda_review = [f for f in lambdas if _contains(f, "REVIEW")]

    high_impact = len(ec2_terminate) + len(unattached_ebs) + len(unused_eips)
    optimization = (
        len(ec2_rightsize)
        + len(gp2_volumes)
        + len(s3_lifecycle)
        + len(rds_review)
        + len(nat_review)
        + len(lambda_review)
    )

    story = []

    story.append(Paragraph("AWS FinOps CFO Executive Report", title_style))
    story.append(Paragraph(
        "Financial visibility, cost exposure, operational risk, and optimization priorities.",
        normal_style
    ))
    story.append(Spacer(1, 12))

    summary_data = [
        ["Metric", "Value"],
        ["AWS Profile", str(report.get("profile"))],
        ["Regions Analyzed", ", ".join(report.get("regions", []))],
        ["Cost Period", f"{cost_summary.get('start', 'N/A')} to {cost_summary.get('end', 'N/A')}"],
        ["Monthly Spend Detected", _money(cost_summary.get("total", 0))],
        ["Estimated Monthly Savings / Exposure", _money(total_savings)],
        ["Total Resources Inventoried", str(total_resources)],
        ["High-Impact Findings", str(high_impact)],
        ["Optimization Findings", str(optimization)],
    ]

    summary_table = Table(summary_data, colWidths=[2.7 * inch, 4.4 * inch])
    summary_table.setStyle(_table_style(header_bg="#111827"))
    story.append(summary_table)

    story.append(Paragraph("1. CFO Summary", section_style))
    story.append(Paragraph(
        "This report identifies cloud cost exposure and near-term optimization opportunities. "
        "The assessment prioritizes immediate cleanup of orphaned resources, controlled optimization "
        "of underutilized workloads, and governance controls to reduce recurring cost drift.",
        normal_style
    ))

    story.append(Paragraph("2. Financial Impact Overview", section_style))

    impact_data = [
        ["Category", "Count", "Financial Interpretation"],
        ["EC2 stop/terminate candidates", str(len(ec2_terminate)), "Potential direct compute savings"],
        ["EC2 rightsizing candidates", str(len(ec2_rightsize)), "Potential recurring optimization"],
        ["Unattached EBS volumes", str(len(unattached_ebs)), "Likely orphaned storage spend"],
        ["Unused Elastic IPs", str(len(unused_eips)), "Low-risk cleanup opportunity"],
        ["S3 lifecycle gaps", str(len(s3_lifecycle)), "Storage tiering opportunity"],
        ["RDS review items", str(len(rds_review)), "Database configuration risk"],
        ["NAT Gateway review items", str(len(nat_review)), "Network cost exposure"],
        ["Lambda tuning items", str(len(lambda_review)), "Serverless efficiency opportunity"],
    ]

    impact_table = Table(impact_data, colWidths=[2.6 * inch, 0.8 * inch, 3.7 * inch])
    impact_table.setStyle(_table_style(header_bg="#1F2937"))
    story.append(impact_table)

    story.append(Paragraph("3. Top Cost Services", section_style))

    services = cost_summary.get("services", [])[:10]

    if services:
        service_data = [["Service", "Cost USD"]]
        for svc in services:
            service_data.append([
                svc.get("service", "N/A"),
                _money(float(svc.get("amount", 0))),
            ])

        service_table = Table(service_data, colWidths=[5.2 * inch, 1.9 * inch])
        service_table.setStyle(_table_style(header_bg="#374151"))
        story.append(service_table)
    else:
        story.append(Paragraph("No Cost Explorer data available.", normal_style))

    story.append(PageBreak())

    story.append(Paragraph("4. Immediate Action Items", section_style))

    immediate_data = [
        ["Priority", "Area", "Finding", "Recommended Action"],
        ["High", "EC2", f"{len(ec2_terminate)} idle candidates", "Validate owner, then stop or terminate"],
        ["High", "EBS", f"{len(unattached_ebs)} unattached volumes", "Snapshot if required, then delete"],
        ["High", "Elastic IP", f"{len(unused_eips)} unused IPs", "Release unused IPs"],
    ]

    immediate_table = Table(immediate_data, colWidths=[0.8 * inch, 1.0 * inch, 2.3 * inch, 3.0 * inch])
    immediate_table.setStyle(_table_style(header_bg="#7F1D1D"))
    story.append(immediate_table)

    story.append(Paragraph("5. Optimization Plan", section_style))

    plan_data = [
        ["Phase", "Action", "Business Control"],
        ["Phase 1", "Remove orphaned resources", "Validate ownership and backups"],
        ["Phase 2", "Rightsize EC2 and migrate GP2 to GP3", "Confirm workload performance"],
        ["Phase 3", "Add S3 lifecycle policies", "Confirm retention requirements"],
        ["Phase 4", "Review RDS, NAT and Lambda configuration", "Confirm application dependency"],
        ["Phase 5", "Enforce governance tags and budgets", "Prevent future drift"],
    ]

    plan_table = Table(plan_data, colWidths=[1.0 * inch, 3.2 * inch, 2.9 * inch])
    plan_table.setStyle(_table_style(header_bg="#065F46"))
    story.append(plan_table)

    story.append(Paragraph("6. Governance Requirements", section_style))
    governance_text = """
    Required governance controls: Owner, Environment, Application, CostCenter, monthly budget thresholds,
    recurring FinOps scans, executive reporting cadence, and remediation approval workflow.
    """
    story.append(Paragraph(governance_text, normal_style))

    story.append(Paragraph("7. Risk Control Statement", section_style))
    risk_text = """
    No production resource should be deleted, resized, stopped, or reconfigured without ownership validation,
    backup verification, rollback plan, and business approval. FinOps is financial governance, not random cleanup.
    """
    story.append(Paragraph(risk_text, normal_style))

    story.append(Spacer(1, 16))
    story.append(Paragraph(
        f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        small_style
    ))

    doc.build(story, onFirstPage=_footer, onLaterPages=_footer)

    return file_path


def _table_style(header_bg="#111827"):
    return TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(header_bg)),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ("TOPPADDING", (0, 0), (-1, 0), 8),

        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, -1), 8),
        ("TEXTCOLOR", (0, 1), (-1, -1), colors.HexColor("#111827")),

        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#D1D5DB")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F9FAFB")]),

        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 1), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 6),
    ])