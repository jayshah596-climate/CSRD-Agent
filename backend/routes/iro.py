from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from database import get_db
from models.iro import IRO, IROType, IRORisk
from models.project import Project
from routes.auth import get_current_user
from models.user import User
from services.iro_service import calculate_iro_score, get_iro_summary, CLIMATE_RISK_TAXONOMY

router = APIRouter(prefix="/projects/{project_id}/iro", tags=["IRO Analysis"])


class IROCreate(BaseModel):
    iro_type: IROType
    risk_type: Optional[IRORisk] = None
    title: str
    description: Optional[str] = None
    esrs_standard: Optional[str] = None
    likelihood_score: Optional[float] = None
    magnitude_score: Optional[float] = None
    velocity_score: Optional[float] = None
    financial_impact_min: Optional[float] = None
    financial_impact_max: Optional[float] = None
    time_horizon: Optional[str] = None
    current_controls: Optional[str] = None
    management_approach: Optional[str] = None
    is_climate_related: Optional[bool] = False


@router.get("")
def list_iros(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _get_project_or_404(db, project_id, current_user)
    iros = db.query(IRO).filter(IRO.project_id == project_id).all()
    return [_iro_to_dict(i) for i in iros]


@router.post("", status_code=201)
def create_iro(
    project_id: str,
    payload: IROCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    project = _get_project_or_404(db, project_id, current_user)

    overall_score = None
    if payload.likelihood_score and payload.magnitude_score:
        overall_score = calculate_iro_score(
            payload.likelihood_score,
            payload.magnitude_score,
            payload.velocity_score or 3.0,
        )

    iro = IRO(
        project_id=project_id,
        company_id=str(project.company_id),
        iro_type=payload.iro_type,
        risk_type=payload.risk_type,
        title=payload.title,
        description=payload.description,
        esrs_standard=payload.esrs_standard,
        likelihood_score=payload.likelihood_score,
        magnitude_score=payload.magnitude_score,
        velocity_score=payload.velocity_score,
        overall_score=overall_score,
        financial_impact_min=payload.financial_impact_min,
        financial_impact_max=payload.financial_impact_max,
        time_horizon=payload.time_horizon,
        current_controls=payload.current_controls,
        management_approach=payload.management_approach,
        is_climate_related=payload.is_climate_related or False,
        is_material=(overall_score or 0) >= 50,
    )
    db.add(iro)
    project.iro_complete = True
    db.commit()
    db.refresh(iro)
    return _iro_to_dict(iro)


@router.delete("/{iro_id}", status_code=204)
def delete_iro(
    project_id: str,
    iro_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _get_project_or_404(db, project_id, current_user)
    iro = db.query(IRO).filter(IRO.id == iro_id, IRO.project_id == project_id).first()
    if not iro:
        raise HTTPException(404, "IRO not found")
    db.delete(iro)
    db.commit()


@router.get("/summary")
def iro_summary(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _get_project_or_404(db, project_id, current_user)
    return get_iro_summary(db, project_id)


@router.get("/risk-taxonomy")
def risk_taxonomy():
    return CLIMATE_RISK_TAXONOMY


def _get_project_or_404(db, project_id, user) -> Project:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(404, "Project not found")
    if str(project.owner_id) != str(user.id):
        raise HTTPException(403, "Access denied")
    return project


def _iro_to_dict(i: IRO) -> dict:
    return {
        "id": str(i.id),
        "iro_type": i.iro_type.value,
        "risk_type": i.risk_type.value if i.risk_type else None,
        "title": i.title,
        "description": i.description,
        "esrs_standard": i.esrs_standard,
        "likelihood_score": i.likelihood_score,
        "magnitude_score": i.magnitude_score,
        "velocity_score": i.velocity_score,
        "overall_score": i.overall_score,
        "financial_impact_min": i.financial_impact_min,
        "financial_impact_max": i.financial_impact_max,
        "financial_impact_currency": i.financial_impact_currency,
        "time_horizon": i.time_horizon,
        "current_controls": i.current_controls,
        "management_approach": i.management_approach,
        "is_material": i.is_material,
        "is_climate_related": i.is_climate_related,
        "created_at": i.created_at.isoformat() if i.created_at else None,
    }
