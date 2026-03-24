from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from database import get_db
from models.project import Project
from routes.auth import get_current_user
from models.user import User
from services.scenario_service import (
    run_scenario_analysis,
    get_all_scenarios,
    calculate_carbon_cost_impact,
    calculate_value_at_risk,
    NGFS_SCENARIOS,
)
from services.emissions_service import get_emission_summary

router = APIRouter(prefix="/projects/{project_id}/scenarios", tags=["Climate Scenarios"])


class ScenarioRequest(BaseModel):
    sector: Optional[str] = "default"
    total_assets_eur_m: Optional[float] = 100.0


@router.get("/ngfs")
def list_ngfs_scenarios():
    return get_all_scenarios()


@router.post("/run")
def run_scenarios(
    project_id: str,
    payload: ScenarioRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    project = _get_project_or_404(db, project_id, current_user)
    emissions = get_emission_summary(db, project_id)

    scope1 = emissions["scope_1"]["total_co2e"]
    scope2 = emissions["scope_2_location"]["total_co2e"]
    scope3 = emissions["scope_3"]["total_co2e"]

    results = run_scenario_analysis(
        scope1=scope1,
        scope2=scope2,
        scope3=scope3,
        total_assets=payload.total_assets_eur_m,
        sector=payload.sector or "default",
    )

    project.scenario_complete = True
    db.commit()

    return {
        "project_id": project_id,
        "input": {
            "scope1_tco2e": scope1,
            "scope2_tco2e": scope2,
            "scope3_tco2e": scope3,
            "total_assets_eur_m": payload.total_assets_eur_m,
            "sector": payload.sector,
        },
        **results,
    }


@router.get("/carbon-cost/{scenario_key}")
def carbon_cost(
    project_id: str,
    scenario_key: str,
    year: int = 2030,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _get_project_or_404(db, project_id, current_user)
    if scenario_key not in NGFS_SCENARIOS:
        raise HTTPException(400, f"Unknown scenario: {scenario_key}")
    emissions = get_emission_summary(db, project_id)

    return calculate_carbon_cost_impact(
        scope1_tco2e=emissions["scope_1"]["total_co2e"],
        scope2_tco2e=emissions["scope_2_location"]["total_co2e"],
        scope3_tco2e=emissions["scope_3"]["total_co2e"],
        scenario_key=scenario_key,
        year=year,
    )


def _get_project_or_404(db, project_id, user) -> Project:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(404, "Project not found")
    if str(project.owner_id) != str(user.id):
        raise HTTPException(403, "Access denied")
    return project
