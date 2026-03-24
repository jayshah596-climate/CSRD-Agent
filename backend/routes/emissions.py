from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List

from database import get_db
from models.emissions import EmissionEntry, EmissionScope
from models.project import Project
from routes.auth import get_current_user
from models.user import User
from services.emissions_service import (
    create_emission_entry,
    get_emission_summary,
    get_scope3_categories,
    DEFAULT_EMISSION_FACTORS,
)

router = APIRouter(prefix="/projects/{project_id}/emissions", tags=["GHG Emissions"])


class EmissionCreate(BaseModel):
    scope: EmissionScope
    source_name: str
    activity_value: float
    activity_unit: str
    emission_factor_value: float
    emission_factor_unit: str
    emission_factor_source: str
    category: Optional[str] = None
    notes: Optional[str] = None


@router.get("")
def list_emissions(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    project = _get_project_or_404(db, project_id, current_user)
    entries = db.query(EmissionEntry).filter(EmissionEntry.project_id == project_id).all()
    return [_entry_to_dict(e) for e in entries]


@router.post("", status_code=201)
def add_emission_entry(
    project_id: str,
    payload: EmissionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    project = _get_project_or_404(db, project_id, current_user)
    entry = create_emission_entry(
        db=db,
        project_id=project_id,
        company_id=str(project.company_id),
        scope=payload.scope,
        source_name=payload.source_name,
        activity_value=payload.activity_value,
        activity_unit=payload.activity_unit,
        emission_factor_value=payload.emission_factor_value,
        emission_factor_unit=payload.emission_factor_unit,
        emission_factor_source=payload.emission_factor_source,
        reporting_year=project.reporting_year,
        category=payload.category,
        notes=payload.notes,
    )
    # Mark emissions step as started
    project.emissions_complete = True
    db.commit()
    return _entry_to_dict(entry)


@router.delete("/{entry_id}", status_code=204)
def delete_emission_entry(
    project_id: str,
    entry_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _get_project_or_404(db, project_id, current_user)
    entry = db.query(EmissionEntry).filter(
        EmissionEntry.id == entry_id,
        EmissionEntry.project_id == project_id,
    ).first()
    if not entry:
        raise HTTPException(404, "Entry not found")
    db.delete(entry)
    db.commit()


@router.get("/summary")
def get_summary(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _get_project_or_404(db, project_id, current_user)
    return get_emission_summary(db, project_id)


@router.get("/scope3-categories")
def scope3_categories():
    return get_scope3_categories()


@router.get("/emission-factors")
def list_emission_factors():
    return [
        {
            "id": key,
            "name": key.replace("_", " ").title(),
            "factor_value": v["factor"],
            "factor_unit": v["unit"],
            "source": v["source"],
        }
        for key, v in DEFAULT_EMISSION_FACTORS.items()
    ]


def _get_project_or_404(db: Session, project_id: str, user: User) -> Project:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(404, "Project not found")
    if str(project.owner_id) != str(user.id):
        raise HTTPException(403, "Access denied")
    return project


def _entry_to_dict(e: EmissionEntry) -> dict:
    return {
        "id": str(e.id),
        "scope": e.scope.value,
        "category": e.category,
        "source_name": e.source_name,
        "activity_value": e.activity_value,
        "activity_unit": e.activity_unit,
        "emission_factor_value": e.emission_factor_value,
        "emission_factor_unit": e.emission_factor_unit,
        "emission_factor_source": e.emission_factor_source,
        "co2e_tonnes": e.co2e_tonnes,
        "reporting_year": e.reporting_year,
        "notes": e.notes,
        "created_at": e.created_at.isoformat() if e.created_at else None,
    }
