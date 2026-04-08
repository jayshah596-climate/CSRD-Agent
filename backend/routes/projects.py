from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import logging

from database import get_db
from models.project import Project, ProjectStatus
from models.company import Company
from routes.auth import get_current_user
from models.user import User

logger = logging.getLogger("csrd-agent")

router = APIRouter(prefix="/projects", tags=["Projects"])


class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    reporting_year: int
    esrs_standards: Optional[List[str]] = None


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ProjectStatus] = None
    esrs_standards: Optional[List[str]] = None


@router.get("")
def list_projects(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    projects = (
        db.query(Project)
        .filter(Project.owner_id == current_user.id)
        .order_by(Project.created_at.desc())
        .all()
    )
    return [_project_to_dict(p) for p in projects]


@router.post("", status_code=201)
def create_project(
    payload: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return _do_create_project(payload, current_user, db)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Project creation failed: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=503,
            detail=f"Database error: {str(e)}. Check /api/debug/db for connectivity status.",
        )


def _do_create_project(payload: ProjectCreate, current_user: User, db: Session):
    if not current_user.company_id:
        # Auto-create a company for the user
        company = Company(
            name=f"{current_user.full_name}'s Company",
            reporting_year=payload.reporting_year,
        )
        db.add(company)
        db.flush()
        current_user.company_id = company.id
        db.flush()

    project = Project(
        name=payload.name,
        description=payload.description,
        reporting_year=payload.reporting_year,
        company_id=current_user.company_id,
        owner_id=current_user.id,
        esrs_standards=payload.esrs_standards or ["E1", "S1", "G1"],
        status=ProjectStatus.DRAFT,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return _project_to_dict(project)


@router.get("/{project_id}")
def get_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    project = _get_project_or_404(db, project_id, current_user)
    return _project_to_dict(project)


@router.put("/{project_id}")
def update_project(
    project_id: str,
    payload: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    project = _get_project_or_404(db, project_id, current_user)
    for field, value in payload.dict(exclude_none=True).items():
        setattr(project, field, value)
    project.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(project)
    return _project_to_dict(project)


@router.delete("/{project_id}", status_code=204)
def delete_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    project = _get_project_or_404(db, project_id, current_user)
    db.delete(project)
    db.commit()


@router.get("/{project_id}/progress")
def get_project_progress(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    project = _get_project_or_404(db, project_id, current_user)
    steps = {
        "data_collection": project.data_collection_complete,
        "materiality": project.materiality_complete,
        "iro": project.iro_complete,
        "emissions": project.emissions_complete,
        "scenario": project.scenario_complete,
        "narrative": project.narrative_complete,
    }
    completed = sum(1 for v in steps.values() if v)
    return {
        "project_id": project_id,
        "steps": steps,
        "completed_steps": completed,
        "total_steps": len(steps),
        "progress_pct": round(completed / len(steps) * 100),
    }


def _get_project_or_404(db: Session, project_id: str, user: User) -> Project:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if str(project.owner_id) != str(user.id):
        raise HTTPException(status_code=403, detail="Access denied")
    return project


def _project_to_dict(p: Project) -> dict:
    return {
        "id": str(p.id),
        "name": p.name,
        "description": p.description,
        "reporting_year": p.reporting_year,
        "status": p.status.value,
        "company_id": str(p.company_id),
        "owner_id": str(p.owner_id),
        "esrs_standards": p.esrs_standards,
        "data_collection_complete": p.data_collection_complete,
        "materiality_complete": p.materiality_complete,
        "iro_complete": p.iro_complete,
        "emissions_complete": p.emissions_complete,
        "scenario_complete": p.scenario_complete,
        "narrative_complete": p.narrative_complete,
        "version": p.version,
        "created_at": p.created_at.isoformat() if p.created_at else None,
        "updated_at": p.updated_at.isoformat() if p.updated_at else None,
    }
