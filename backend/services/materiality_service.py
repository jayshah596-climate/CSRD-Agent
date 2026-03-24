from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from models.materiality import MaterialityTopic, MaterialityAssessment
import math


# ESRS 2025 standard topics for Double Materiality Assessment
ESRS_TOPICS = [
    # Environmental
    {"standard": "E1", "topic": "Climate change", "sub_topics": ["Climate change mitigation", "Climate change adaptation", "Energy"]},
    {"standard": "E2", "topic": "Pollution", "sub_topics": ["Pollution of air", "Pollution of water", "Pollution of soil", "Pollution of living organisms and food resources", "Substances of concern"]},
    {"standard": "E3", "topic": "Water and marine resources", "sub_topics": ["Water consumption", "Water withdrawals", "Marine resources"]},
    {"standard": "E4", "topic": "Biodiversity and ecosystems", "sub_topics": ["Direct impact drivers", "Impacts on the state of species", "Impacts on the extent and condition of ecosystems", "Impacts and dependencies on ecosystem services"]},
    {"standard": "E5", "topic": "Resource use and circular economy", "sub_topics": ["Resources inflows including waste", "Resource outflows related to products and services", "Waste"]},
    # Social
    {"standard": "S1", "topic": "Own workforce", "sub_topics": ["Working conditions", "Equal treatment and opportunities", "Other work-related rights"]},
    {"standard": "S2", "topic": "Workers in the value chain", "sub_topics": ["Working conditions", "Equal treatment and opportunities", "Other work-related rights"]},
    {"standard": "S3", "topic": "Affected communities", "sub_topics": ["Communities' economic, social and cultural rights", "Communities' civil and political rights", "Rights of indigenous peoples"]},
    {"standard": "S4", "topic": "Consumers and end-users", "sub_topics": ["Information-related impacts", "Personal safety and security", "Social inclusion"]},
    # Governance
    {"standard": "G1", "topic": "Business conduct", "sub_topics": ["Corporate culture and business conduct", "Management of relationships with suppliers", "Corruption and bribery", "Political engagement and lobbying"]},
]


def calculate_impact_score(
    scale: float,
    scope: float,
    irremediability: float,
    likelihood: float,
    is_negative: bool = True,
) -> float:
    """
    Calculate impact materiality score using ESRS DMA methodology.
    Scale: 1-5, Scope: 1-5, Irremediability: 1-5 (for negative), Likelihood: 1-5
    """
    if is_negative:
        # For actual negative impacts: scale * scope * irremediability
        severity = (scale * scope * irremediability) ** (1 / 3)  # geometric mean
    else:
        # For positive impacts: scale * scope
        severity = math.sqrt(scale * scope)

    # Weighted with likelihood for potential impacts
    score = (severity * 0.7 + likelihood * 0.3) * 20  # normalize to 0-100
    return min(round(score, 2), 100.0)


def calculate_financial_score(magnitude: float, likelihood: float) -> float:
    """Calculate financial materiality score."""
    score = (magnitude * likelihood / 25) * 100
    return min(round(score, 2), 100.0)


def is_material(impact_score: float, financial_score: float, threshold: float = 40.0) -> bool:
    """Determine if a topic is material based on either dimension."""
    return impact_score >= threshold or financial_score >= threshold


def generate_heatmap_data(topics: List[MaterialityTopic]) -> Dict[str, Any]:
    """Generate heatmap visualization data from materiality topics."""
    data_points = []
    for topic in topics:
        if topic.impact_score is not None and topic.financial_score is not None:
            data_points.append({
                "id": str(topic.id),
                "label": topic.esrs_topic,
                "esrs_standard": topic.esrs_standard,
                "x": round(topic.financial_score, 1),  # financial materiality axis
                "y": round(topic.impact_score, 1),  # impact materiality axis
                "is_material": topic.is_material,
            })

    return {
        "data_points": data_points,
        "threshold": 40.0,
        "x_label": "Financial Materiality",
        "y_label": "Impact Materiality",
        "quadrants": {
            "top_right": "High Priority (Dual Material)",
            "top_left": "Impact Material",
            "bottom_right": "Financially Material",
            "bottom_left": "Not Material",
        },
    }


def get_material_topics(db: Session, project_id: str) -> List[MaterialityTopic]:
    return (
        db.query(MaterialityTopic)
        .filter(
            MaterialityTopic.project_id == project_id,
            MaterialityTopic.is_material == True,
        )
        .order_by(MaterialityTopic.impact_score.desc())
        .all()
    )


def create_default_topics(db: Session, project_id: str, company_id: str) -> List[MaterialityTopic]:
    """Create default ESRS topic assessments for a new project."""
    topics = []
    for esrs_topic in ESRS_TOPICS:
        topic = MaterialityTopic(
            project_id=project_id,
            company_id=company_id,
            esrs_standard=esrs_topic["standard"],
            esrs_topic=esrs_topic["topic"],
            impact_score=0.0,
            financial_score=0.0,
            is_material=False,
        )
        db.add(topic)
        topics.append(topic)
    db.commit()
    return topics
