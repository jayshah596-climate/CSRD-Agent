import os
import json
import uuid
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from database import get_db
from models.report import Report, ReportStatus
from models.project import Project
from models.company import Company
from models.materiality import MaterialityTopic
from routes.auth import get_current_user
from models.user import User
from services.report_service import (
    generate_pdf_report,
    generate_excel_report,
    generate_json_export,
)
from services.ai_narrative_service import (
    generate_full_report_narratives,
    ESRS_REPORT_SECTIONS,
)
from services.emissions_service import get_emission_summary
from xbrl_engine.generator import generate_xbrl_instance, generate_taxonomy_mapping
from config import settings

router = APIRouter(prefix="/projects/{project_id}/reports", tags=["Reports"])

REPORTS_DIR = "/tmp/csrd_reports"
os.makedirs(REPORTS_DIR, exist_ok=True)


class ReportGenerateRequest(BaseModel):
    title: Optional[str] = None
    sections: Optional[List[str]] = None
    include_xbrl: Optional[bool] = True


@router.get("")
def list_reports(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _get_project_or_404(db, project_id, current_user)
    reports = db.query(Report).filter(Report.project_id == project_id).order_by(Report.created_at.desc()).all()
    return [_report_to_dict(r) for r in reports]


@router.post("/generate", status_code=202)
def generate_report(
    project_id: str,
    payload: ReportGenerateRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    project = _get_project_or_404(db, project_id, current_user)
    company = db.query(Company).filter(Company.id == project.company_id).first()

    title = payload.title or f"{company.name if company else 'Company'} CSRD Report {project.reporting_year}"

    report = Report(
        project_id=project_id,
        company_id=str(project.company_id),
        title=title,
        reporting_year=project.reporting_year,
        status=ReportStatus.GENERATING,
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    background_tasks.add_task(
        _generate_report_background,
        report_id=str(report.id),
        project_id=project_id,
        sections=payload.sections or ESRS_REPORT_SECTIONS,
        include_xbrl=payload.include_xbrl,
    )

    return {
        "report_id": str(report.id),
        "status": "generating",
        "message": "Report generation started. Check /reports/{id} for status.",
    }


@router.get("/{report_id}")
def get_report(
    project_id: str,
    report_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _get_project_or_404(db, project_id, current_user)
    report = db.query(Report).filter(
        Report.id == report_id, Report.project_id == project_id
    ).first()
    if not report:
        raise HTTPException(404, "Report not found")
    return _report_to_dict(report)


@router.get("/{report_id}/download/{format}")
def download_report(
    project_id: str,
    report_id: str,
    format: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _get_project_or_404(db, project_id, current_user)
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(404, "Report not found")

    format_map = {
        "pdf": report.pdf_url,
        "excel": report.excel_url,
        "json": report.json_url,
        "xbrl": report.xbrl_url,
    }
    file_path = format_map.get(format)
    if not file_path or not os.path.exists(file_path):
        raise HTTPException(404, f"{format.upper()} file not yet generated")

    media_types = {
        "pdf": "application/pdf",
        "excel": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "json": "application/json",
        "xbrl": "application/xml",
    }
    return FileResponse(
        path=file_path,
        media_type=media_types.get(format, "application/octet-stream"),
        filename=os.path.basename(file_path),
    )


@router.get("/{report_id}/xbrl-mapping")
def get_xbrl_mapping(
    project_id: str,
    report_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _get_project_or_404(db, project_id, current_user)
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(404, "Report not found")
    return generate_taxonomy_mapping(report.report_content or {})


def _generate_report_background(
    report_id: str,
    project_id: str,
    sections: List[str],
    include_xbrl: bool,
):
    """Background task to generate all report formats."""
    from database import SessionLocal

    db = SessionLocal()
    try:
        report = db.query(Report).filter(Report.id == report_id).first()
        project = db.query(Project).filter(Project.id == project_id).first()
        company = db.query(Company).filter(Company.id == project.company_id).first()

        company_dict = _company_to_dict(company)
        project_dict = {
            "id": str(project.id),
            "name": project.name,
            "reporting_year": project.reporting_year,
        }

        # Collect report data
        emissions = get_emission_summary(db, project_id)
        materiality_topics = db.query(MaterialityTopic).filter(
            MaterialityTopic.project_id == project_id
        ).all()

        material_topic_names = [t.esrs_topic for t in materiality_topics if t.is_material]

        report_data = {
            "emissions": emissions,
            "workforce": {
                "total_employees": company_dict.get("employee_count"),
                "female_pct": None,
                "ltir": None,
                "gender_pay_gap": None,
                "training_hours": None,
            },
            "materiality": {
                "topics": [
                    {
                        "esrs_standard": t.esrs_standard,
                        "esrs_topic": t.esrs_topic,
                        "impact_score": t.impact_score,
                        "financial_score": t.financial_score,
                        "is_material": t.is_material,
                    }
                    for t in materiality_topics
                ]
            },
        }

        # Generate AI narratives
        context = {
            "company_name": company_dict.get("name", "the company"),
            "sector": company_dict.get("sector", "N/A"),
            "employee_count": company_dict.get("employee_count", "N/A"),
            "annual_revenue": company_dict.get("annual_revenue", "N/A"),
            "reporting_year": project.reporting_year,
            "material_topics": material_topic_names,
            "total_scope12_tco2e": round(
                emissions["scope_1"]["total_co2e"] + emissions["scope_2_location"]["total_co2e"], 1
            ),
            "total_scope3_tco2e": round(emissions["scope_3"]["total_co2e"], 1),
            "emission_reduction_target": 50,
            "target_year": 2030,
            "base_year": 2019,
            "governance_body": "Board Sustainability Committee",
            "materiality_level": "high",
            "country_count": 1,
            "gender_pay_gap": "N/A",
            "ltir": "N/A",
            "board_members": "N/A",
            "independent_members": "N/A",
            "female_board_pct": "N/A",
            "compliance_training_pct": "N/A",
        }
        narratives = generate_full_report_narratives(
            context=context,
            sections=sections,
            api_key=settings.ANTHROPIC_API_KEY or None,
        )

        report_data["narratives"] = narratives
        report.report_content = report_data
        report.esrs_disclosures = {s: narratives.get(s, "") for s in sections}

        base_path = os.path.join(REPORTS_DIR, report_id)

        # PDF
        try:
            pdf_path = f"{base_path}.pdf"
            generate_pdf_report(company_dict, project_dict, report_data, narratives, pdf_path)
            report.pdf_url = pdf_path
        except Exception as e:
            report.generation_log = report.generation_log or []
            if isinstance(report.generation_log, list):
                report.generation_log.append(f"PDF error: {str(e)}")

        # Excel
        try:
            xlsx_path = f"{base_path}.xlsx"
            generate_excel_report(company_dict, project_dict, report_data, xlsx_path)
            report.excel_url = xlsx_path
        except Exception as e:
            if isinstance(report.generation_log, list):
                report.generation_log.append(f"Excel error: {str(e)}")

        # JSON
        try:
            json_export = generate_json_export(company_dict, project_dict, report_data, narratives)
            json_path = f"{base_path}.json"
            with open(json_path, "w") as f:
                json.dump(json_export, f, indent=2)
            report.json_url = json_path
        except Exception as e:
            if isinstance(report.generation_log, list):
                report.generation_log.append(f"JSON error: {str(e)}")

        # XBRL
        if include_xbrl:
            try:
                xbrl_content = generate_xbrl_instance(
                    company_dict, report_data, project.reporting_year
                )
                xbrl_path = f"{base_path}.xbrl"
                with open(xbrl_path, "w") as f:
                    f.write(xbrl_content)
                report.xbrl_url = xbrl_path
            except Exception as e:
                if isinstance(report.generation_log, list):
                    report.generation_log.append(f"XBRL error: {str(e)}")

        report.status = ReportStatus.FINAL
        report.narrative_complete = True
        project.narrative_complete = True
        db.commit()

    except Exception as e:
        db.query(Report).filter(Report.id == report_id).update(
            {"status": ReportStatus.FAILED}
        )
        db.commit()
    finally:
        db.close()


def _get_project_or_404(db, project_id, user) -> Project:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(404, "Project not found")
    if str(project.owner_id) != str(user.id):
        raise HTTPException(403, "Access denied")
    return project


def _report_to_dict(r: Report) -> dict:
    return {
        "id": str(r.id),
        "project_id": str(r.project_id),
        "title": r.title,
        "reporting_year": r.reporting_year,
        "status": r.status.value,
        "version": r.version,
        "pdf_available": r.pdf_url is not None and os.path.exists(r.pdf_url or ""),
        "excel_available": r.excel_url is not None and os.path.exists(r.excel_url or ""),
        "json_available": r.json_url is not None and os.path.exists(r.json_url or ""),
        "xbrl_available": r.xbrl_url is not None and os.path.exists(r.xbrl_url or ""),
        "created_at": r.created_at.isoformat() if r.created_at else None,
        "updated_at": r.updated_at.isoformat() if r.updated_at else None,
    }


def _company_to_dict(c: Company) -> dict:
    if not c:
        return {}
    return {
        "id": str(c.id),
        "name": c.name,
        "legal_name": c.legal_name,
        "lei_code": c.lei_code,
        "sector": c.sector,
        "nace_code": c.nace_code,
        "country": c.country,
        "employee_count": c.employee_count,
        "annual_revenue": c.annual_revenue,
        "total_assets": c.total_assets,
    }
