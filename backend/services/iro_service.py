from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from models.iro import IRO, IRORisk, IROType


# NGFS/TCFD-aligned physical and transition risk taxonomy
CLIMATE_RISK_TAXONOMY = {
    "physical_acute": [
        "Increased severity of extreme weather events (cyclones, floods, droughts)",
        "Wildfire risk in operating regions",
        "Extreme heat events affecting operations",
        "Coastal flooding from sea-level rise",
    ],
    "physical_chronic": [
        "Chronic temperature increase affecting energy demand",
        "Changes in precipitation patterns affecting water availability",
        "Sea-level rise impacting coastal assets",
        "Ocean acidification affecting marine operations",
    ],
    "transition_policy": [
        "Carbon pricing mechanisms (ETS, carbon tax)",
        "Enhanced emissions reporting requirements (CSRD/ESRS)",
        "Mandatory climate disclosure regulations",
        "Product efficiency standards and regulations",
        "Phase-out of fossil fuel subsidies",
    ],
    "transition_technology": [
        "Cost decrease of renewable energy displacing fossil fuels",
        "Electrification of industrial processes",
        "Hydrogen economy transition",
        "Battery storage technology disruption",
        "Carbon capture and storage cost trajectories",
    ],
    "transition_market": [
        "Changing customer preferences toward low-carbon products",
        "Increased cost of raw materials due to carbon pricing",
        "Shifts in energy supply and demand",
        "Revaluation of assets (stranded asset risk)",
    ],
    "transition_reputational": [
        "Stigmatization of carbon-intensive sectors",
        "Increased investor ESG scrutiny",
        "Consumer boycotts due to sustainability practices",
        "Employee attraction and retention challenges",
    ],
}


CLIMATE_OPPORTUNITIES = [
    "Renewable energy adoption reducing operating costs",
    "Green product/service innovation",
    "Access to green financing and sustainability-linked bonds",
    "Energy efficiency improvements",
    "Carbon credit generation from nature-based solutions",
    "New markets from climate adaptation services",
]


def calculate_iro_score(likelihood: float, magnitude: float, velocity: float = 3.0) -> float:
    """Calculate overall IRO risk/opportunity score (0-100)."""
    raw = (likelihood * 0.4 + magnitude * 0.4 + velocity * 0.2) * 20
    return min(round(raw, 2), 100.0)


def get_iro_summary(db: Session, project_id: str) -> Dict[str, Any]:
    iros = db.query(IRO).filter(IRO.project_id == project_id).all()

    summary = {
        "total": len(iros),
        "by_type": {
            "impact": 0,
            "risk": 0,
            "opportunity": 0,
        },
        "by_risk_type": {},
        "material_count": 0,
        "climate_related_count": 0,
        "high_priority": [],
        "financial_exposure": {
            "min": 0.0,
            "max": 0.0,
            "currency": "EUR",
        },
    }

    for iro in iros:
        summary["by_type"][iro.iro_type.value] += 1
        if iro.is_material:
            summary["material_count"] += 1
        if iro.is_climate_related:
            summary["climate_related_count"] += 1
        if iro.risk_type:
            rt = iro.risk_type.value
            summary["by_risk_type"][rt] = summary["by_risk_type"].get(rt, 0) + 1
        if iro.overall_score and iro.overall_score >= 60:
            summary["high_priority"].append({
                "id": str(iro.id),
                "title": iro.title,
                "type": iro.iro_type.value,
                "score": iro.overall_score,
                "time_horizon": iro.time_horizon,
            })
        if iro.financial_impact_min:
            summary["financial_exposure"]["min"] += iro.financial_impact_min
        if iro.financial_impact_max:
            summary["financial_exposure"]["max"] += iro.financial_impact_max

    summary["high_priority"] = sorted(
        summary["high_priority"], key=lambda x: x["score"], reverse=True
    )[:5]

    return summary
