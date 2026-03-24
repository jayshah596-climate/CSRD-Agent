from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Any

from database import get_db
from models.data_collection import DataCollectionEntry
from models.project import Project
from routes.auth import get_current_user
from models.user import User
from esrs_engine.mapping import get_esrs_structure, map_data_to_esrs
from esrs_engine.validator import validate_project_data

router = APIRouter(prefix="/projects/{project_id}/data", tags=["Data Collection"])


class DataPointCreate(BaseModel):
    esrs_standard: str
    esrs_disclosure: Optional[str] = None
    datapoint_id: Optional[str] = None
    datapoint_name: str
    data_type: str
    value_numeric: Optional[float] = None
    value_text: Optional[str] = None
    value_boolean: Optional[bool] = None
    unit: Optional[str] = None
    source_type: Optional[str] = "manual"
    is_estimated: Optional[bool] = False
    notes: Optional[str] = None


@router.get("")
def list_data_entries(
    project_id: str,
    esrs_standard: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _get_project_or_404(db, project_id, current_user)
    q = db.query(DataCollectionEntry).filter(DataCollectionEntry.project_id == project_id)
    if esrs_standard:
        q = q.filter(DataCollectionEntry.esrs_standard == esrs_standard)
    return [_entry_to_dict(e) for e in q.all()]


@router.post("", status_code=201)
def create_data_entry(
    project_id: str,
    payload: DataPointCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    project = _get_project_or_404(db, project_id, current_user)
    entry = DataCollectionEntry(
        project_id=project_id,
        company_id=str(project.company_id),
        **payload.dict(),
    )
    db.add(entry)
    project.data_collection_complete = True
    db.commit()
    db.refresh(entry)
    return _entry_to_dict(entry)


@router.put("/{entry_id}")
def update_data_entry(
    project_id: str,
    entry_id: str,
    payload: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _get_project_or_404(db, project_id, current_user)
    entry = db.query(DataCollectionEntry).filter(
        DataCollectionEntry.id == entry_id,
        DataCollectionEntry.project_id == project_id,
    ).first()
    if not entry:
        raise HTTPException(404, "Entry not found")
    allowed = {"value_numeric", "value_text", "value_boolean", "notes", "is_estimated", "unit"}
    for k, v in payload.items():
        if k in allowed:
            setattr(entry, k, v)
    db.commit()
    db.refresh(entry)
    return _entry_to_dict(entry)


@router.get("/esrs-structure")
def esrs_structure():
    return get_esrs_structure()


@router.get("/validate")
def validate_data(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _get_project_or_404(db, project_id, current_user)
    entries = db.query(DataCollectionEntry).filter(
        DataCollectionEntry.project_id == project_id
    ).all()

    data_dict = {}
    for e in entries:
        if e.datapoint_id:
            data_dict[e.datapoint_id] = e.value_numeric or e.value_text or e.value_boolean

    return validate_project_data(data_dict)


def _get_project_or_404(db, project_id, user) -> Project:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(404, "Project not found")
    if str(project.owner_id) != str(user.id):
        raise HTTPException(403, "Access denied")
    return project


def _entry_to_dict(e: DataCollectionEntry) -> dict:
    return {
        "id": str(e.id),
        "esrs_standard": e.esrs_standard,
        "esrs_disclosure": e.esrs_disclosure,
        "datapoint_id": e.datapoint_id,
        "datapoint_name": e.datapoint_name,
        "data_type": e.data_type,
        "value_numeric": e.value_numeric,
        "value_text": e.value_text,
        "value_boolean": e.value_boolean,
        "unit": e.unit,
        "source_type": e.source_type,
        "is_estimated": e.is_estimated,
        "is_validated": e.is_validated,
        "notes": e.notes,
        "created_at": e.created_at.isoformat() if e.created_at else None,
    }
