from typing import List, Dict, Optional, Any
from sqlalchemy.orm import Session
from models.emissions import EmissionEntry, EmissionScope, EmissionFactor
from models.project import Project
import uuid


# Default emission factors (kgCO2e per unit) - representative values
DEFAULT_EMISSION_FACTORS = {
    # Scope 1 - Stationary Combustion
    "natural_gas": {"factor": 2.034, "unit": "kgCO2e/m3", "source": "DEFRA 2023"},
    "diesel": {"factor": 2.687, "unit": "kgCO2e/litre", "source": "DEFRA 2023"},
    "petrol": {"factor": 2.310, "unit": "kgCO2e/litre", "source": "DEFRA 2023"},
    "coal": {"factor": 2340.0, "unit": "kgCO2e/tonne", "source": "DEFRA 2023"},
    "lpg": {"factor": 1.555, "unit": "kgCO2e/litre", "source": "DEFRA 2023"},
    # Scope 2 - Electricity (EU average)
    "electricity_eu": {"factor": 0.276, "unit": "kgCO2e/kWh", "source": "EEA 2023"},
    "electricity_uk": {"factor": 0.207, "unit": "kgCO2e/kWh", "source": "DEFRA 2023"},
    "electricity_us": {"factor": 0.386, "unit": "kgCO2e/kWh", "source": "EPA 2023"},
    # Scope 3 - Business Travel
    "flight_short_haul": {"factor": 0.255, "unit": "kgCO2e/km/passenger", "source": "DEFRA 2023"},
    "flight_long_haul": {"factor": 0.195, "unit": "kgCO2e/km/passenger", "source": "DEFRA 2023"},
    "rail_travel": {"factor": 0.037, "unit": "kgCO2e/km/passenger", "source": "DEFRA 2023"},
    "car_petrol": {"factor": 0.170, "unit": "kgCO2e/km", "source": "DEFRA 2023"},
    "car_diesel": {"factor": 0.161, "unit": "kgCO2e/km", "source": "DEFRA 2023"},
    # Scope 3 - Purchased goods
    "steel": {"factor": 2100.0, "unit": "kgCO2e/tonne", "source": "IPCC 2023"},
    "cement": {"factor": 820.0, "unit": "kgCO2e/tonne", "source": "IPCC 2023"},
    "aluminum": {"factor": 11500.0, "unit": "kgCO2e/tonne", "source": "IPCC 2023"},
    "paper": {"factor": 921.0, "unit": "kgCO2e/tonne", "source": "IPCC 2023"},
}


def calculate_emission(
    activity_value: float,
    emission_factor: float,
    activity_unit: str,
    factor_unit: str,
) -> float:
    """Calculate CO2e in tonnes from activity data."""
    # Convert kg to tonnes
    co2e_kg = activity_value * emission_factor
    return co2e_kg / 1000.0


def get_emission_summary(db: Session, project_id: str) -> Dict[str, Any]:
    """Get aggregated emission summary for a project."""
    entries = (
        db.query(EmissionEntry)
        .filter(EmissionEntry.project_id == project_id)
        .all()
    )

    summary = {
        "scope_1": {"total_co2e": 0.0, "entries": 0},
        "scope_2_location": {"total_co2e": 0.0, "entries": 0},
        "scope_2_market": {"total_co2e": 0.0, "entries": 0},
        "scope_3": {"total_co2e": 0.0, "entries": 0, "by_category": {}},
        "total_co2e": 0.0,
        "intensity_metrics": {},
    }

    for entry in entries:
        if entry.co2e_tonnes is None:
            continue
        scope_key = entry.scope.value
        summary[scope_key]["total_co2e"] += entry.co2e_tonnes
        summary[scope_key]["entries"] += 1

        if entry.scope == EmissionScope.SCOPE_3 and entry.category:
            cat = entry.category
            if cat not in summary["scope_3"]["by_category"]:
                summary["scope_3"]["by_category"][cat] = 0.0
            summary["scope_3"]["by_category"][cat] += entry.co2e_tonnes

    summary["total_co2e"] = (
        summary["scope_1"]["total_co2e"]
        + summary["scope_2_location"]["total_co2e"]
        + summary["scope_3"]["total_co2e"]
    )

    return summary


def create_emission_entry(
    db: Session,
    project_id: str,
    company_id: str,
    scope: EmissionScope,
    source_name: str,
    activity_value: float,
    activity_unit: str,
    emission_factor_value: float,
    emission_factor_unit: str,
    emission_factor_source: str,
    reporting_year: int,
    category: Optional[str] = None,
    notes: Optional[str] = None,
) -> EmissionEntry:
    co2e = calculate_emission(activity_value, emission_factor_value, activity_unit, emission_factor_unit)

    entry = EmissionEntry(
        project_id=project_id,
        company_id=company_id,
        scope=scope,
        category=category,
        source_name=source_name,
        activity_value=activity_value,
        activity_unit=activity_unit,
        emission_factor_value=emission_factor_value,
        emission_factor_unit=emission_factor_unit,
        emission_factor_source=emission_factor_source,
        co2e_tonnes=co2e,
        reporting_year=reporting_year,
        notes=notes,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def get_scope3_categories() -> List[Dict[str, str]]:
    """Return all 15 GHG Protocol Scope 3 categories."""
    return [
        {"id": "cat1", "name": "Purchased goods and services"},
        {"id": "cat2", "name": "Capital goods"},
        {"id": "cat3", "name": "Fuel and energy related activities"},
        {"id": "cat4", "name": "Upstream transportation and distribution"},
        {"id": "cat5", "name": "Waste generated in operations"},
        {"id": "cat6", "name": "Business travel"},
        {"id": "cat7", "name": "Employee commuting"},
        {"id": "cat8", "name": "Upstream leased assets"},
        {"id": "cat9", "name": "Downstream transportation and distribution"},
        {"id": "cat10", "name": "Processing of sold products"},
        {"id": "cat11", "name": "Use of sold products"},
        {"id": "cat12", "name": "End-of-life treatment of sold products"},
        {"id": "cat13", "name": "Downstream leased assets"},
        {"id": "cat14", "name": "Franchises"},
        {"id": "cat15", "name": "Investments"},
    ]
