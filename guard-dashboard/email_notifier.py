"""
Email Notification Service for GUARD Anomaly Detection System.
GUARD: Generative Understanding for Anomaly Response & Detection

Sends HTML-formatted email alerts when anomalies are detected, with PDF attachments
matching the RCA (Root Cause Analysis) format.
"""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from datetime import datetime
import pandas as pd
from typing import List, Dict
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import io


# ── Email Configuration ────────────────────────────────────────────
# Set these environment variables or modify defaults:
#   SMTP_SERVER   - SMTP server address (default: smtp.gmail.com)
#   SMTP_PORT     - SMTP port (default: 587)
#   SMTP_USERNAME - Email account username
#   SMTP_PASSWORD - Email account password or app-specific password
#   ALERT_FROM    - Sender email address
#   ALERT_TO      - Comma-separated list of recipient emails

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
ALERT_FROM = os.getenv("ALERT_FROM", SMTP_USERNAME)
ALERT_TO = os.getenv("ALERT_TO", "").split(",")

# System and Equipment configuration
SYSTEM_NAME = "GUARD (Generative Understanding for Anomaly Response & Detection)"
EQUIPMENT_NAME = "BOOSTER COMPRESSOR B CPP DONGGI"
FIELD_NAME = "CPP Donggi"
MODEL_SYSTEM = "J.BEC-UAD"


def get_top_contributors(row: pd.Series, top_n: int = 5) -> List[Dict]:
    """
    Extract top N contributing variables from anomaly row.

    Returns list of dicts with:
      - variable: parameter name
      - tag: sensor tag
      - value: actual value
      - expected: predicted/normal value
      - deviation: actual - predicted
      - deviation_pct: percentage deviation
      - contribution: % contribution to reconstruction loss
    """
    from rule_engine import THRESHOLDS

    contributors = []

    for param, config in THRESHOLDS.items():
        contrib_col = f"contrib_{param}"
        dev_col = f"dev_{param}"

        if contrib_col not in row or dev_col not in row:
            continue

        value = row.get(param, 0)
        deviation = row.get(dev_col, 0)
        contribution = row.get(contrib_col, 0)

        # Convert string values to float
        try:
            if isinstance(value, str):
                value = float(value.replace('%', '').replace(',', ''))
            if isinstance(deviation, str):
                deviation = float(deviation.replace('%', '').replace(',', ''))
            if isinstance(contribution, str):
                contribution = float(contribution.replace('%', '').replace(',', ''))
        except (ValueError, AttributeError):
            pass

        expected = value - deviation

        # Calculate percentage deviation
        if expected != 0:
            deviation_pct = (deviation / expected) * 100
        else:
            deviation_pct = 0

        contributors.append({
            "variable": param,
            "tag": config["tag"],
            "value": float(value) if value else 0,
            "expected": float(expected) if expected else 0,
            "deviation": float(deviation) if deviation else 0,
            "deviation_pct": float(deviation_pct) if deviation_pct else 0,
            "contribution": float(contribution) if contribution else 0,
            "unit": config["unit"],
        })

    # Sort by contribution (highest first)
    contributors.sort(key=lambda x: abs(x["contribution"]), reverse=True)

    return contributors[:top_n]


def generate_rca_pdf(row: pd.Series, equipment_name: str = EQUIPMENT_NAME) -> bytes:
    """
    Generate comprehensive RCA (Root Cause Analysis) PDF report matching the Excel format.
    Includes division categorization, probable causes, actions, and affected variables.
    Returns PDF as bytes for email attachment.
    """
    from rca_knowledge_base import get_applicable_rca_scenarios, get_division_summary
    from rule_engine import THRESHOLDS

    buffer = io.BytesIO()

    # Create PDF in landscape orientation
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4),
                           topMargin=0.4*inch, bottomMargin=0.4*inch,
                           leftMargin=0.3*inch, rightMargin=0.3*inch)

    elements = []
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=12,
        textColor=colors.HexColor('#1976d2'),
        spaceAfter=8,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )

    # Title
    title = Paragraph("ANOMALY DETECTION BOOSTER COMPRESSOR B CPP DONGGI", title_style)
    elements.append(title)
    elements.append(Spacer(1, 0.15*inch))

    # Header information
    timestamp = row.name
    if isinstance(timestamp, pd.Timestamp):
        timestamp_str = timestamp.strftime("%d %B %Y")
    else:
        timestamp_str = str(timestamp)

    header_data = [
        ["Equipment:", EQUIPMENT_NAME, "Timestamp:", timestamp_str],
        ["Location:", FIELD_NAME, "", ""],
    ]

    header_table = Table(header_data, colWidths=[1*inch, 3.2*inch, 1*inch, 2.3*inch])
    header_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))

    elements.append(header_table)
    elements.append(Spacer(1, 0.15*inch))

    # ═══════════════════════════════════════════════════════════
    # TABLE 1: Original Sensor Values Table
    # ═══════════════════════════════════════════════════════════

    # Get top contributors
    contributors = get_top_contributors(row, top_n=5)

    # Sensor values table
    sensor_table_data = [
        ["VARIABLE", "TAG", "ACTUAL\nVALUE", "EXPECTED\nVALUE", "DEVIATION", "DEVIATION\n%", "LOSS\nCONTRIBUTION", "ABNORMALITY"]
    ]

    for c in contributors:
        # Determine abnormality status (matching modal view logic)
        # Get threshold config for this variable
        variable_name = c['variable']
        threshold_config = THRESHOLDS.get(variable_name, {})

        # Check if value is outside normal range
        is_outside_range = False
        if threshold_config:
            low = threshold_config.get('low', 0)
            high = threshold_config.get('high', 0)
            is_outside_range = (c['value'] < low) or (c['value'] > high)

        # Check for significant deviation or high contribution
        is_significant_deviation = abs(c['deviation_pct']) > 2.0  # Lower threshold: 2% deviation
        has_high_contribution = c['contribution'] > 20.0  # High contribution to loss

        # Abnormality is YES if ANY condition is met
        abnormality = "YES" if (is_outside_range or is_significant_deviation or has_high_contribution) else "NO"

        sensor_table_data.append([
            c['variable'].replace('_', ' '),
            c['tag'],
            f"{c['value']:.2f}",
            f"{c['expected']:.2f}",
            f"{c['deviation']:.2f}",
            f"{c['deviation_pct']:+.1f}%",
            f"{c['contribution']:.1f}%",
            abnormality
        ])

    # Create sensor table
    sensor_col_widths = [1.3*inch, 0.9*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.9*inch, 0.9*inch]
    sensor_table = Table(sensor_table_data, colWidths=sensor_col_widths, repeatRows=1)

    # Sensor table styling
    sensor_table.setStyle(TableStyle([
        # Header row
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4472C4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),

        # Data rows
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('ALIGN', (2, 1), (6, -1), 'RIGHT'),
        ('ALIGN', (7, 1), (7, -1), 'CENTER'),
        ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),

        # Grid
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BOX', (0, 0), (-1, -1), 1.5, colors.black),

        # Alternating row colors
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F2F2F2')]),
    ]))

    elements.append(sensor_table)
    elements.append(Spacer(1, 0.2*inch))

    # ═══════════════════════════════════════════════════════════
    # TABLE 2: RCA Division Table
    # ═══════════════════════════════════════════════════════════

    # Get applicable RCA scenarios based on anomaly
    scenarios = get_applicable_rca_scenarios(row, top_n=8)

    if len(scenarios) == 0:
        # Fallback if no scenarios match
        scenarios = [{
            "division": "GENERAL",
            "division_code": 999,
            "color": "#FFFFFF",
            "id": "GEN-0",
            "probable": "General Anomaly Detected",
            "rca": "Process parameters deviate from normal operating conditions. Detailed investigation required.",
            "actions": "Review all sensor readings. Compare with historical trends. Perform detailed root cause analysis.",
            "variables": {
                "Flow_Rate": True,
                "Suction_Pressure": True,
                "Discharge_Pressure": True,
                "Suction_Temperature": True,
                "Discharge_Temperature": True
            },
            "symptom": "Abnormal process conditions detected by LSTM anomaly detection model.",
            "symptom_code": "ANOMALY",
            "abnormal_sensors": {}
        }]

    # Main RCA table (without CODE column)
    table_data = [
        ["SYMPTOM", "SUB", "PROB", "RCA", "ACTIONS",
         Paragraph("<b>Flow<br/>Rate</b>", ParagraphStyle('center', fontSize=7, alignment=TA_CENTER)),
         Paragraph("<b>Suction<br/>Press</b>", ParagraphStyle('center', fontSize=7, alignment=TA_CENTER)),
         Paragraph("<b>Discharge<br/>Press</b>", ParagraphStyle('center', fontSize=7, alignment=TA_CENTER)),
         Paragraph("<b>Suction<br/>Temp</b>", ParagraphStyle('center', fontSize=7, alignment=TA_CENTER)),
         Paragraph("<b>Discharge<br/>Temp</b>", ParagraphStyle('center', fontSize=7, alignment=TA_CENTER)),
         "SYMPTOM"]
    ]

    # Track rows for coloring by division
    division_rows = {}
    current_row = 1  # Start after header

    # Group scenarios by division
    from collections import defaultdict
    scenarios_by_division = defaultdict(list)
    for scenario in scenarios:
        scenarios_by_division[scenario["division"]].append(scenario)

    # Build table rows grouped by division
    for division_name in ["INSTRUMENT", "PROCESS", "MECHANICAL", "ELECTRICAL", "RELATIONAL"]:
        if division_name not in scenarios_by_division:
            continue

        div_scenarios = scenarios_by_division[division_name]
        division_start_row = current_row

        for idx, scenario in enumerate(div_scenarios):
            # RCA text (wrapped)
            rca_para = Paragraph(scenario["rca"], ParagraphStyle('rca', fontSize=6, leading=7))

            # Actions text (wrapped)
            actions_para = Paragraph(scenario["actions"], ParagraphStyle('actions', fontSize=6, leading=7))

            # Symptom text (wrapped)
            symptom_para = Paragraph(scenario["symptom"], ParagraphStyle('symptom', fontSize=6, leading=7))

            # Variable checkmarks
            vars_dict = scenario["variables"]

            table_data.append([
                division_name if idx == 0 else "",  # Division name only on first row
                scenario["division_code"] if idx == 0 else "",  # Code only on first row
                scenario["id"].split('-')[1],  # Probable number (e.g., "0" from "INST-0")
                rca_para,
                actions_para,
                "YES" if vars_dict.get("Flow_Rate", False) else "NO",
                "YES" if vars_dict.get("Suction_Pressure", False) else "NO",
                "YES" if vars_dict.get("Discharge_Pressure", False) else "NO",
                "YES" if vars_dict.get("Suction_Temperature", False) else "NO",
                "YES" if vars_dict.get("Discharge_Temperature", False) else "NO",
                symptom_para
            ])
            current_row += 1

        division_rows[division_name] = (division_start_row, current_row - 1, div_scenarios[0]["color"])

    # Add summary row
    threshold_ratio = row.get("threshold_ratio", 0)
    exceed_percent = row.get("exceed_percent", 0)
    gas_loss = row.get("Gas_Loss_MMSCF", 0)

    # Convert string values to float
    try:
        if isinstance(threshold_ratio, str):
            threshold_ratio = float(threshold_ratio.replace('%', '').replace(',', ''))
        if isinstance(exceed_percent, str):
            exceed_percent = float(exceed_percent.replace('%', '').replace(',', ''))
        if isinstance(gas_loss, str):
            gas_loss = float(gas_loss.replace('%', '').replace(',', ''))
    except (ValueError, AttributeError):
        pass

    # Get division summary
    div_summary = get_division_summary(scenarios)
    div_summary_text = ", ".join([f"{div}: {count}" for div, count in div_summary.items()])

    summary_text = (
        f"<b>Anomaly Detection Summary:</b> Reconstruction loss exceeds threshold by {exceed_percent:.1f}% "
        f"(Threshold ratio: {threshold_ratio:.1f}%). Estimated gas loss: {gas_loss:.3f} MMSCF. "
        f"<b>Divisions Impacted:</b> {div_summary_text}"
    )

    table_data.append([
        Paragraph("<b>SUMMARY</b>", ParagraphStyle('summary', fontSize=7, fontName='Helvetica-Bold')),
        "", "", "", "",
        "", "", "", "", "",
        Paragraph(summary_text, ParagraphStyle('summary', fontSize=6, leading=7))
    ])

    # Create table (11 columns now, removed CODE column)
    col_widths = [0.9*inch, 0.4*inch, 0.35*inch, 2.0*inch, 2.0*inch,
                  0.45*inch, 0.45*inch, 0.45*inch, 0.45*inch, 0.45*inch,
                  1.8*inch]

    rca_table = Table(table_data, colWidths=col_widths, repeatRows=1)

    # Base table styling
    style_list = [
        # Header row
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4472C4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 7),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),

        # Data rows
        ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -2), 6),
        ('ALIGN', (0, 1), (2, -2), 'CENTER'),
        ('ALIGN', (5, 1), (9, -2), 'CENTER'),
        ('VALIGN', (0, 1), (-1, -1), 'TOP'),

        # Summary row
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#E7E6E6')),
        ('FONTNAME', (0, -1), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -1), (-1, -1), 6),
        ('SPAN', (1, -1), (9, -1)),  # Span columns 1-9 (middle columns)

        # Grid
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BOX', (0, 0), (-1, -1), 1.5, colors.black),
    ]

    # Add division-specific row coloring and spanning
    for div_name, (start_row, end_row, color_hex) in division_rows.items():
        # Background color for division
        style_list.append(('BACKGROUND', (0, start_row), (-1, end_row), colors.HexColor(color_hex)))

        # Span division name and code across multiple rows if needed
        if end_row > start_row:
            style_list.append(('SPAN', (0, start_row), (0, end_row)))  # Division name
            style_list.append(('SPAN', (1, start_row), (1, end_row)))  # Division code

    rca_table.setStyle(TableStyle(style_list))

    elements.append(rca_table)
    elements.append(Spacer(1, 0.15*inch))

    # Footer
    footer_text = (
        f"<b>Generated by:</b> {SYSTEM_NAME} | "
        f"<b>Date:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | "
        f"<b>Scenarios Evaluated:</b> {len(scenarios)}"
    )
    footer = Paragraph(footer_text, ParagraphStyle('footer', fontSize=7))
    elements.append(footer)

    # Build PDF
    doc.build(elements)

    # Get PDF bytes
    pdf_bytes = buffer.getvalue()
    buffer.close()

    return pdf_bytes


def build_email_html(row: pd.Series, equipment_name: str = EQUIPMENT_NAME) -> str:
    """Build HTML email content matching the mobile app format."""

    timestamp = row.name
    if isinstance(timestamp, pd.Timestamp):
        timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
    else:
        timestamp_str = str(timestamp)

    threshold_ratio = row.get("threshold_ratio", 0)
    exceed_percent = row.get("exceed_percent", 0)
    asset_status = row.get("asset_integrity_status", "N/A")

    # Convert string values to float
    try:
        if isinstance(threshold_ratio, str):
            threshold_ratio = float(threshold_ratio.replace('%', '').replace(',', ''))
        if isinstance(exceed_percent, str):
            exceed_percent = float(exceed_percent.replace('%', '').replace(',', ''))
    except (ValueError, AttributeError):
        pass

    # Get top contributors
    contributors = get_top_contributors(row, top_n=5)

    # Build contributor table rows
    table_rows = []
    for c in contributors:
        table_rows.append(f"""
        <tr>
            <td style="padding: 12px; border-bottom: 1px solid #e0e0e0;">
                <strong>{c['variable']}</strong><br>
                <span style="color: #666; font-size: 12px;">{c['tag']}</span>
            </td>
            <td style="padding: 12px; border-bottom: 1px solid #e0e0e0; text-align: right;">
                {c['value']:.2f}
            </td>
            <td style="padding: 12px; border-bottom: 1px solid #e0e0e0; text-align: right;">
                {c['expected']:.2f}
            </td>
            <td style="padding: 12px; border-bottom: 1px solid #e0e0e0; text-align: right;">
                {c['deviation']:.2f}<br>
                <span style="color: {'#d32f2f' if c['deviation'] > 0 else '#388e3c'}; font-size: 12px;">
                    ({c['deviation_pct']:+.1f}%)
                </span>
            </td>
            <td style="padding: 12px; border-bottom: 1px solid #e0e0e0; text-align: right;">
                <strong>{c['contribution']:.1f}%</strong>
            </td>
        </tr>
        """)

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;">
        <div style="max-width: 800px; margin: 0 auto; background-color: #ffffff;">

            <!-- Header -->
            <div style="background-color: #1976d2; color: white; padding: 20px;">
                <h1 style="margin: 0; font-size: 18px; font-weight: 500;">
                    [{FIELD_NAME}] ANOMALY DETECTION - {equipment_name}
                </h1>
                <p style="margin: 8px 0 0 0; font-size: 12px; opacity: 0.9;">
                    {SYSTEM_NAME}
                </p>
            </div>

            <!-- Content -->
            <div style="padding: 24px;">

                <p style="color: #333; line-height: 1.6; margin-bottom: 24px;">
                    An abnormal condition has been detected in the process parameters of the
                    <strong>{equipment_name}</strong>. The details are as follows:
                </p>

                <!-- Anomaly Details -->
                <h2 style="color: #333; font-size: 20px; margin-bottom: 16px; margin-top: 32px;">
                    Anomaly Details
                </h2>

                <ul style="list-style: none; padding: 0;">
                    <li style="margin-bottom: 12px;">
                        <strong>Timestamp:</strong> {timestamp_str}
                    </li>
                    <li style="margin-bottom: 12px;">
                        <strong>Threshold ratio:</strong> {threshold_ratio:.1f}%
                        <span style="color: #d32f2f;">
                            (Reconstruction loss exceeds threshold by {exceed_percent:.1f}%)
                        </span>
                    </li>
                    <li style="margin-bottom: 12px;">
                        <strong>Asset integrity status:</strong> {asset_status}
                    </li>
                </ul>

                <!-- Contributors Table -->
                <p style="color: #333; margin-top: 32px; margin-bottom: 16px;">
                    The main contributing variables and their deviations from normal operating conditions are listed below:
                </p>

                <table style="width: 100%; border-collapse: collapse; margin-top: 16px; background-color: #fafafa;">
                    <thead>
                        <tr style="background-color: #e0e0e0;">
                            <th style="padding: 12px; text-align: left; font-weight: 600; border-bottom: 2px solid #bdbdbd;">
                                Variable
                            </th>
                            <th style="padding: 12px; text-align: right; font-weight: 600; border-bottom: 2px solid #bdbdbd;">
                                Value
                            </th>
                            <th style="padding: 12px; text-align: right; font-weight: 600; border-bottom: 2px solid #bdbdbd;">
                                Expected<br>Normal<br>Value
                            </th>
                            <th style="padding: 12px; text-align: right; font-weight: 600; border-bottom: 2px solid #bdbdbd;">
                                Deviation
                            </th>
                            <th style="padding: 12px; text-align: right; font-weight: 600; border-bottom: 2px solid #bdbdbd;">
                                Loss<br>Contribution
                            </th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join(table_rows)}
                    </tbody>
                </table>

                <p style="color: #666; font-size: 12px; margin-top: 16px; font-style: italic;">
                    *Contribution represents the percentage of total reconstruction error attributed to each variable.
                </p>

                <!-- Footer -->
                <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #e0e0e0;">
                    <p style="color: #666; font-size: 12px; margin: 0;">
                        This is an automated alert from {SYSTEM_NAME}.
                    </p>
                    <p style="color: #666; font-size: 12px; margin: 8px 0 0 0;">
                        Generated at: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
                    </p>
                </div>

            </div>
        </div>
    </body>
    </html>
    """

    return html


def send_email_alert(
    row: pd.Series,
    recipients: List[str] = None,
    equipment_name: str = EQUIPMENT_NAME,
    smtp_server: str = SMTP_SERVER,
    smtp_port: int = SMTP_PORT,
    username: str = SMTP_USERNAME,
    password: str = SMTP_PASSWORD,
    from_addr: str = ALERT_FROM,
) -> bool:
    """
    Send anomaly alert email.

    Parameters:
      - row: Anomaly data row from pipeline
      - recipients: List of email addresses (uses ALERT_TO env var if None)
      - equipment_name: Equipment name for subject line
      - smtp_*: SMTP configuration (uses env vars by default)

    Returns:
      - True if email sent successfully, False otherwise
    """

    if recipients is None:
        recipients = ALERT_TO

    # Filter out empty recipients
    recipients = [r.strip() for r in recipients if r.strip()]

    if not recipients:
        print("Warning: No email recipients configured. Set ALERT_TO environment variable.")
        return False

    if not username or not password:
        print("Warning: SMTP credentials not configured. Set SMTP_USERNAME and SMTP_PASSWORD.")
        return False

    # Build email
    msg = MIMEMultipart("mixed")
    msg["Subject"] = f"[{FIELD_NAME}] ANOMALY DETECTION - {equipment_name}"
    msg["From"] = from_addr
    msg["To"] = ", ".join(recipients)

    # Create HTML content
    html_content = build_email_html(row, equipment_name)

    # Attach HTML part
    html_part = MIMEText(html_content, "html")
    msg.attach(html_part)

    # Generate and attach PDF
    try:
        pdf_bytes = generate_rca_pdf(row, equipment_name)

        # Get timestamp for filename
        timestamp = row.name
        if isinstance(timestamp, pd.Timestamp):
            timestamp_str = timestamp.strftime("%Y%m%d_%H%M%S")
        else:
            timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")

        pdf_filename = f"RCA_Report_{timestamp_str}.pdf"

        pdf_part = MIMEApplication(pdf_bytes, _subtype="pdf")
        pdf_part.add_header('Content-Disposition', 'attachment', filename=pdf_filename)
        msg.attach(pdf_part)
    except Exception as e:
        print(f"Warning: Failed to generate PDF attachment: {e}")

    # Send email
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(username, password)
        server.send_message(msg)
        server.quit()
        print(f"✓ Alert email sent to: {', '.join(recipients)}")
        return True
    except Exception as e:
        print(f"✗ Failed to send email: {e}")
        return False


def send_batch_alerts(
    anomalies: pd.DataFrame,
    max_alerts: int = None,
    **email_config
) -> Dict[str, int]:
    """
    Send email alerts for multiple anomalies.

    Parameters:
      - anomalies: DataFrame of anomaly rows
      - max_alerts: Maximum number of alerts to send (None = all)
      - **email_config: Override email configuration (recipients, smtp_*, etc.)

    Returns:
      - Dict with counts: {"sent": N, "failed": M, "total": T}
    """

    if max_alerts:
        batch = anomalies.head(max_alerts)
    else:
        batch = anomalies

    results = {"sent": 0, "failed": 0, "total": len(batch)}

    print(f"\nSending {len(batch)} anomaly alert(s)...")

    for idx, row in batch.iterrows():
        print(f"\n  [{idx}]", end=" ")
        success = send_email_alert(row, **email_config)
        if success:
            results["sent"] += 1
        else:
            results["failed"] += 1

    print(f"\n\nEmail Alert Summary:")
    print(f"  Total: {results['total']}")
    print(f"  Sent:  {results['sent']}")
    print(f"  Failed: {results['failed']}")

    return results
