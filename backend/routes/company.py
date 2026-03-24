from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from database import get_db
from models.company import Company
from routes.auth import get_current_user
from models.user import User

router = APIRouter(prefix="/company", tags=["Company"])


class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    legal_name: Optional[str] = None
    nace_code: Optional[str] = None
    sector: Optional[str] = None
    sub_sector: Optional[str] = None
    employee_count: Optional[int] = None
    annual_revenue: Optional[float] = None
    total_assets: Optional[float] = None
    country: Optional[str] = None
    headquarters_address: Optional[str] = None
    reporting_year: Optional[int] = None
    lei_code: Optional[str] = None
    website: Optional[str] = None
    sustainability_contact_email: Optional[str] = None


@router.get("")
def get_company(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not current_user.company_id:
        raise HTTPException(404, "No company linked to user")
    company = db.query(Company).filter(Company.id == current_user.company_id).first()
    if not company:
        raise HTTPException(404, "Company not found")
    return _company_to_dict(company)


@router.put("")
def update_company(
    payload: CompanyUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not current_user.company_id:
        raise HTTPException(404, "No company linked to user")
    company = db.query(Company).filter(Company.id == current_user.company_id).first()
    if not company:
        raise HTTPException(404, "Company not found")

    for field, value in payload.dict(exclude_none=True).items():
        setattr(company, field, value)
    db.commit()
    db.refresh(company)
    return _company_to_dict(company)


def _company_to_dict(c: Company) -> dict:
    return {
        "id": str(c.id),
        "name": c.name,
        "legal_name": c.legal_name,
        "registration_number": c.registration_number,
        "lei_code": c.lei_code,
        "nace_code": c.nace_code,
        "sector": c.sector,
        "sub_sector": c.sub_sector,
        "employee_count": c.employee_count,
        "annual_revenue": c.annual_revenue,
        "total_assets": c.total_assets,
        "country": c.country,
        "headquarters_address": c.headquarters_address,
        "website": c.website,
        "sustainability_contact_email": c.sustainability_contact_email,
        "reporting_year": c.reporting_year,
        "created_at": c.created_at.isoformat() if c.created_at else None,
    }
