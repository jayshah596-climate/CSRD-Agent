"""
Report Generation Service
Generates PDF, Excel, JSON, and Web reports for CSRD compliance.
"""

import io
import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.lib import colors
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        PageBreak, HRFlowable,
    )
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
    _REPORTLAB_AVAILABLE = True
except ImportError:
    _REPORTLAB_AVAILABLE = False

try:
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter
    _OPENPYXL_AVAILABLE = True
except ImportError:
    _OPENPYXL_AVAILABLE = False


def generate_pdf_report(
    company: Dict[str, Any],
    project: Dict[str, Any],
    report_data: Dict[str, Any],
    narratives: Dict[str, str],
    output_path: str,
) -> str:
    """Generate a structured PDF report compliant with ESRS 2025."""
    if not _REPORTLAB_AVAILABLE:
        raise RuntimeError("ReportLab not installed. Run: pip install reportlab")

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    styles = getSampleStyleSheet()
    story = []

    # Custom styles
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Title"],
        fontSize=24,
        spaceAfter=12,
        textColor=colors.HexColor("#1e3a5f"),
        fontName="Helvetica-Bold",
    )
    heading1_style = ParagraphStyle(
        "Heading1Custom",
        parent=styles["Heading1"],
        fontSize=16,
        spaceBefore=20,
        spaceAfter=8,
        textColor=colors.HexColor("#1e3a5f"),
        fontName="Helvetica-Bold",
    )
    heading2_style = ParagraphStyle(
        "Heading2Custom",
        parent=styles["Heading2"],
        fontSize=13,
        spaceBefore=14,
        spaceAfter=6,
        textColor=colors.HexColor("#2d6a4f"),
        fontName="Helvetica-Bold",
    )
    body_style = ParagraphStyle(
        "BodyCustom",
        parent=styles["Normal"],
        fontSize=10,
        spaceAfter=8,
        alignment=TA_JUSTIFY,
        fontName="Helvetica",
    )
    table_header_style = ParagraphStyle(
        "TableHeader",
        parent=styles["Normal"],
        fontSize=9,
        textColor=colors.white,
        fontName="Helvetica-Bold",
    )

    # ─── Cover Page ────────────────────────────────────────────────
    story.append(Spacer(1, 3 * cm))
    story.append(Paragraph(
        f"{company.get('name', 'Company Name')}",
        title_style,
    ))
    story.append(Paragraph(
        f"Sustainability Report {project.get('reporting_year', datetime.now().year)}",
        ParagraphStyle(
            "SubTitle",
            parent=styles["Normal"],
            fontSize=18,
            spaceAfter=8,
            textColor=colors.HexColor("#2d6a4f"),
        ),
    ))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#1e3a5f")))
    story.append(Spacer(1, 0.5 * cm))
    story.append(Paragraph(
        "Prepared in accordance with ESRS (European Sustainability Reporting Standards) "
        "as required under CSRD (Corporate Sustainability Reporting Directive) "
        "EU Commission Delegated Regulation 2023/2772",
        ParagraphStyle(
            "SubText",
            parent=styles["Normal"],
            fontSize=11,
            spaceAfter=8,
            textColor=colors.HexColor("#555555"),
            alignment=TA_LEFT,
        ),
    ))
    story.append(Spacer(1, 1 * cm))

    # Company info table
    info_data = [
        ["Company", company.get("name", "N/A")],
        ["Legal Name", company.get("legal_name", "N/A")],
        ["Sector", company.get("sector", "N/A")],
        ["NACE Code", company.get("nace_code", "N/A")],
        ["Country", company.get("country", "N/A")],
        ["Reporting Year", str(project.get("reporting_year", "N/A"))],
        ["Report Date", datetime.now().strftime("%d %B %Y")],
    ]
    info_table = Table(info_data, colWidths=[5 * cm, 11 * cm])
    info_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#e8f4f8")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(info_table)
    story.append(PageBreak())

    # ─── Table of Contents ─────────────────────────────────────────
    story.append(Paragraph("Table of Contents", heading1_style))
    toc_items = [
        "1. Executive Summary",
        "2. General Disclosures (ESRS 2)",
        "3. Climate Change (ESRS E1)",
        "4. GHG Emissions",
        "5. Social – Own Workforce (ESRS S1)",
        "6. Governance and Business Conduct (ESRS G1)",
        "7. Double Materiality Assessment",
        "8. Climate Scenario Analysis",
        "9. Key Performance Indicators",
        "10. Appendix – Methodology",
    ]
    for item in toc_items:
        story.append(Paragraph(item, body_style))
    story.append(PageBreak())

    # ─── Executive Summary ─────────────────────────────────────────
    story.append(Paragraph("1. Executive Summary", heading1_style))
    exec_summary = narratives.get("General Disclosure", report_data.get("executive_summary", ""))
    story.append(Paragraph(exec_summary or "Executive summary to be completed.", body_style))
    story.append(Spacer(1, 0.5 * cm))

    # ─── GHG Emissions ─────────────────────────────────────────────
    story.append(Paragraph("4. GHG Emissions (ESRS E1-6)", heading1_style))
    story.append(Paragraph(
        narratives.get("E1 GHG Emissions", "Emissions data as reported below."),
        body_style,
    ))

    emissions = report_data.get("emissions", {})
    emissions_data = [
        [Paragraph("Emission Category", table_header_style),
         Paragraph("tCO2e", table_header_style),
         Paragraph("% of Total", table_header_style)],
    ]
    total_ghg = max(emissions.get("total_co2e", 1), 1)
    rows = [
        ("Scope 1 – Direct Emissions", emissions.get("scope_1", {}).get("total_co2e", 0)),
        ("Scope 2 – Indirect (Location-based)", emissions.get("scope_2_location", {}).get("total_co2e", 0)),
        ("Scope 2 – Indirect (Market-based)", emissions.get("scope_2_market", {}).get("total_co2e", 0)),
        ("Scope 3 – Value Chain", emissions.get("scope_3", {}).get("total_co2e", 0)),
        ("Total GHG Emissions", emissions.get("total_co2e", 0)),
    ]
    for label, value in rows:
        pct = round(value / total_ghg * 100, 1) if total_ghg > 0 else 0
        emissions_data.append([label, f"{value:,.1f}", f"{pct}%"])

    emissions_table = Table(emissions_data, colWidths=[9 * cm, 4 * cm, 4 * cm])
    emissions_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e3a5f")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.white, colors.HexColor("#f5f5f5")]),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#e8f4f8")),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("PADDING", (0, 0), (-1, -1), 6),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
    ]))
    story.append(emissions_table)
    story.append(PageBreak())

    # ─── Workforce ─────────────────────────────────────────────────
    story.append(Paragraph("5. Own Workforce (ESRS S1)", heading1_style))
    story.append(Paragraph(
        narratives.get("S1 Own Workforce", "Workforce data as reported below."),
        body_style,
    ))

    workforce = report_data.get("workforce", {})
    wf_data = [
        [Paragraph("KPI", table_header_style),
         Paragraph("Value", table_header_style),
         Paragraph("Unit", table_header_style)],
        ["Total Employees", str(workforce.get("total_employees", "N/A")), "Headcount"],
        ["Female Employees %", str(workforce.get("female_pct", "N/A")), "%"],
        ["Lost Time Injury Rate", str(workforce.get("ltir", "N/A")), "per M hours"],
        ["Gender Pay Gap", str(workforce.get("gender_pay_gap", "N/A")), "%"],
        ["Training Hours per FTE", str(workforce.get("training_hours", "N/A")), "Hours"],
    ]
    wf_table = Table(wf_data, colWidths=[9 * cm, 4 * cm, 4 * cm])
    wf_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2d6a4f")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f5f5")]),
        ("PADDING", (0, 0), (-1, -1), 6),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
    ]))
    story.append(wf_table)
    story.append(PageBreak())

    # ─── Governance ────────────────────────────────────────────────
    story.append(Paragraph("6. Governance and Business Conduct (ESRS G1)", heading1_style))
    story.append(Paragraph(
        narratives.get("G1 Governance", "Governance data as reported below."),
        body_style,
    ))
    story.append(PageBreak())

    # ─── Methodology ───────────────────────────────────────────────
    story.append(Paragraph("10. Appendix – Methodology", heading1_style))
    methodology_text = """
This report has been prepared in accordance with ESRS Set 1 (EU Commission Delegated Regulation
2023/2772) under the Corporate Sustainability Reporting Directive (CSRD, Directive 2022/2464/EU).

GHG emissions have been calculated in accordance with the GHG Protocol Corporate Accounting and
Reporting Standard. Emission factors are sourced from DEFRA (2023), EEA (2023), and IPCC AR6.

The Double Materiality Assessment was conducted following EFRAG's Implementation Guidance on
Materiality Assessment (IG 1, 2023), with stakeholder engagement as per ESRS 2 SBM-2.

Climate scenario analysis is based on NGFS Phase 4 scenarios (2023 vintage).
"""
    story.append(Paragraph(methodology_text.strip(), body_style))

    doc.build(story)
    return output_path


def generate_excel_report(
    company: Dict[str, Any],
    project: Dict[str, Any],
    report_data: Dict[str, Any],
    output_path: str,
) -> str:
    """Generate Excel report with multiple worksheets."""
    if not _OPENPYXL_AVAILABLE:
        raise RuntimeError("openpyxl not installed. Run: pip install openpyxl")

    wb = openpyxl.Workbook()

    # Styles
    header_fill = PatternFill(start_color="1e3a5f", end_color="1e3a5f", fill_type="solid")
    green_fill = PatternFill(start_color="2d6a4f", end_color="2d6a4f", fill_type="solid")
    light_fill = PatternFill(start_color="e8f4f8", end_color="e8f4f8", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF", size=11)
    bold_font = Font(bold=True, size=10)
    center_align = Alignment(horizontal="center", vertical="center")

    # ── Sheet 1: Summary ────────────────────────────────────────────
    ws = wb.active
    ws.title = "Summary"
    ws.column_dimensions["A"].width = 35
    ws.column_dimensions["B"].width = 20

    ws["A1"] = f"{company.get('name', 'Company')} - CSRD Sustainability Report {project.get('reporting_year', 2023)}"
    ws["A1"].font = Font(bold=True, size=14, color="1e3a5f")
    ws.merge_cells("A1:D1")

    ws["A3"] = "Company"
    ws["B3"] = company.get("name", "N/A")
    ws["A4"] = "Sector"
    ws["B4"] = company.get("sector", "N/A")
    ws["A5"] = "Reporting Year"
    ws["B5"] = project.get("reporting_year", "N/A")
    ws["A6"] = "Report Generated"
    ws["B6"] = datetime.now().strftime("%Y-%m-%d")

    for row in range(3, 7):
        ws[f"A{row}"].font = bold_font
        ws[f"A{row}"].fill = light_fill

    # ── Sheet 2: GHG Emissions ─────────────────────────────────────
    ws_e = wb.create_sheet("E1 GHG Emissions")
    ws_e.column_dimensions["A"].width = 40
    ws_e.column_dimensions["B"].width = 20
    ws_e.column_dimensions["C"].width = 15

    headers = ["Emission Category", "tCO2e", "% of Total"]
    for col, h in enumerate(headers, 1):
        cell = ws_e.cell(row=1, column=col, value=h)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = center_align

    emissions = report_data.get("emissions", {})
    total = max(emissions.get("total_co2e", 1), 1)
    rows = [
        ("Scope 1 – Direct Emissions", emissions.get("scope_1", {}).get("total_co2e", 0)),
        ("Scope 2 – Location-based", emissions.get("scope_2_location", {}).get("total_co2e", 0)),
        ("Scope 2 – Market-based", emissions.get("scope_2_market", {}).get("total_co2e", 0)),
        ("Scope 3 – Total Value Chain", emissions.get("scope_3", {}).get("total_co2e", 0)),
        ("Total GHG Emissions", emissions.get("total_co2e", 0)),
    ]
    for i, (label, value) in enumerate(rows, 2):
        ws_e.cell(row=i, column=1, value=label)
        ws_e.cell(row=i, column=2, value=round(value, 2))
        ws_e.cell(row=i, column=3, value=f"{round(value/total*100,1)}%")
        if i % 2 == 0:
            for col in range(1, 4):
                ws_e.cell(row=i, column=col).fill = light_fill

    # ── Sheet 3: Workforce ─────────────────────────────────────────
    ws_s = wb.create_sheet("S1 Workforce")
    ws_s.column_dimensions["A"].width = 35
    ws_s.column_dimensions["B"].width = 20
    ws_s.column_dimensions["C"].width = 15

    s_headers = ["KPI", "Value", "Unit"]
    for col, h in enumerate(s_headers, 1):
        cell = ws_s.cell(row=1, column=col, value=h)
        cell.fill = green_fill
        cell.font = header_font
        cell.alignment = center_align

    workforce = report_data.get("workforce", {})
    wf_rows = [
        ("Total Employees", workforce.get("total_employees", "N/A"), "Headcount"),
        ("Female Employees %", workforce.get("female_pct", "N/A"), "%"),
        ("Lost Time Injury Rate", workforce.get("ltir", "N/A"), "per M hours"),
        ("Fatalities", workforce.get("fatalities", 0), "Count"),
        ("Gender Pay Gap (unadjusted)", workforce.get("gender_pay_gap", "N/A"), "%"),
        ("Training Hours per FTE", workforce.get("training_hours", "N/A"), "Hours"),
        ("Employee Turnover Rate", workforce.get("turnover_rate", "N/A"), "%"),
        ("Collective Bargaining Coverage", workforce.get("bargaining_coverage", "N/A"), "%"),
    ]
    for i, (label, value, unit) in enumerate(wf_rows, 2):
        ws_s.cell(row=i, column=1, value=label)
        ws_s.cell(row=i, column=2, value=value)
        ws_s.cell(row=i, column=3, value=unit)
        if i % 2 == 0:
            for col in range(1, 4):
                ws_s.cell(row=i, column=col).fill = light_fill

    # ── Sheet 4: Materiality ───────────────────────────────────────
    ws_m = wb.create_sheet("Materiality Assessment")
    ws_m.column_dimensions["A"].width = 12
    ws_m.column_dimensions["B"].width = 30
    ws_m.column_dimensions["C"].width = 18
    ws_m.column_dimensions["D"].width = 18
    ws_m.column_dimensions["E"].width = 12

    m_headers = ["ESRS", "Topic", "Impact Score", "Financial Score", "Material?"]
    for col, h in enumerate(m_headers, 1):
        cell = ws_m.cell(row=1, column=col, value=h)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = center_align

    materiality = report_data.get("materiality", {}).get("topics", [])
    for i, topic in enumerate(materiality, 2):
        ws_m.cell(row=i, column=1, value=topic.get("esrs_standard", ""))
        ws_m.cell(row=i, column=2, value=topic.get("esrs_topic", ""))
        ws_m.cell(row=i, column=3, value=topic.get("impact_score", ""))
        ws_m.cell(row=i, column=4, value=topic.get("financial_score", ""))
        ws_m.cell(row=i, column=5, value="Yes" if topic.get("is_material") else "No")

    wb.save(output_path)
    return output_path


def generate_json_export(
    company: Dict[str, Any],
    project: Dict[str, Any],
    report_data: Dict[str, Any],
    narratives: Dict[str, str],
) -> Dict[str, Any]:
    """Generate structured JSON export of full ESRS report."""
    return {
        "schema_version": "ESRS-2025-1.0",
        "generated_at": datetime.now().isoformat(),
        "company": company,
        "project": {
            "id": project.get("id"),
            "name": project.get("name"),
            "reporting_year": project.get("reporting_year"),
        },
        "disclosures": {
            "general": {
                "standard": "ESRS 2",
                "narrative": narratives.get("General Disclosure", ""),
            },
            "environmental": {
                "E1": {
                    "climate_policy": narratives.get("E1 Climate Policy", ""),
                    "strategy": narratives.get("E1 Strategy", ""),
                    "emissions": report_data.get("emissions", {}),
                    "energy": report_data.get("energy", {}),
                },
                "E2": {"pollution": report_data.get("pollution", {})},
                "E3": {"water": report_data.get("water", {})},
                "E4": {"biodiversity": report_data.get("biodiversity", {})},
                "E5": {"circular_economy": report_data.get("circular_economy", {})},
            },
            "social": {
                "S1": {
                    "workforce_narrative": narratives.get("S1 Own Workforce", ""),
                    "workforce_data": report_data.get("workforce", {}),
                },
                "S2": report_data.get("value_chain_workers", {}),
                "S3": report_data.get("communities", {}),
                "S4": report_data.get("consumers", {}),
            },
            "governance": {
                "G1": {
                    "governance_narrative": narratives.get("G1 Governance", ""),
                    "governance_data": report_data.get("governance", {}),
                },
            },
        },
        "scenario_analysis": report_data.get("scenarios", {}),
        "materiality_assessment": report_data.get("materiality", {}),
        "methodology": {
            "reporting_standard": "ESRS Set 1 (EU 2023/2772)",
            "ghg_protocol": "GHG Protocol Corporate Standard",
            "scenario_framework": "NGFS Phase 4 (2023)",
            "materiality_framework": "EFRAG DMA Implementation Guidance",
        },
    }
