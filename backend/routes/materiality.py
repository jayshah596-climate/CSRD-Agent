from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List

from database import get_db
from models.materiality import MaterialityTopic, MaterialityAssessment
from models.project import Project
from routes.auth import get_current_user
from models.user import User
from services.materiality_service import (
    calculate_impact_score,
    calculate_financial_score,
    is_material,
    generate_heatmap_data,
    get_material_topics,
    create_default_topics,
    ESRS_TOPICS,
)

router = APIRouter(prefix="/projects/{project_id}/materiality", tags=["Materiality"])


class TopicScore(BaseModel):
    topic_id: str
    impact_scale: Optional[float] = None
    impact_scope: Optional[float] = None
    impact_irremediability: Optional[float] = None
    impact_likelihood: Optional[float] = None
    financial_magnitude: Optional[float] = None
    financial_likelihood: Optional[float] = None
    is_positive_impact: Optional[bool] = False
    time_horizon: Optional[str] = None
    materiality_rationale: Optional[str] = None


@router.get("/topics")
def list_topics(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _get_project_or_404(db, project_id, current_user)
    topics = db.query(MaterialityTopic).filter(
        MaterialityTopic.project_id == project_id
    ).all()

    if not topics:
        # Initialize default topics
        project = db.query(Project).filter(Project.id == project_id).first()
        topics = create_default_topics(db, project_id, str(project.company_id))

    return [_topic_to_dict(t) for t in topics]


@router.get("/esrs-topics")
def get_esrs_topics():
    return ESRS_TOPICS


@router.put("/topics/{topic_id}")
def update_topic_score(
    project_id: str,
    topic_id: str,
    payload: TopicScore,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _get_project_or_404(db, project_id, current_user)
    topic = db.query(MaterialityTopic).filter(
        MaterialityTopic.id == topic_id,
        MaterialityTopic.project_id == project_id,
    ).first()
    if not topic:
        raise HTTPException(404, "Topic not found")

    # Update scores
    for field, value in payload.dict(exclude_none=True, exclude={"topic_id"}).items():
        setattr(topic, field, value)

    # Recalculate composite scores
    if all(v is not None for v in [topic.impact_scale, topic.impact_scope, topic.impact_likelihood]):
        topic.impact_score = calculate_impact_score(
            scale=topic.impact_scale or 1,
            scope=topic.impact_scope or 1,
            irremediability=topic.impact_irremediability or 3,
            likelihood=topic.impact_likelihood or 3,
            is_negative=not (topic.is_positive_impact or False),
        )

    if topic.financial_magnitude is not None and topic.financial_likelihood is not None:
        topic.financial_score = calculate_financial_score(
            topic.financial_magnitude, topic.financial_likelihood
        )

    topic.is_material = is_material(
        topic.impact_score or 0.0,
        topic.financial_score or 0.0,
    )

    db.commit()
    db.refresh(topic)
    return _topic_to_dict(topic)


@router.get("/heatmap")
def get_heatmap(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _get_project_or_404(db, project_id, current_user)
    topics = db.query(MaterialityTopic).filter(
        MaterialityTopic.project_id == project_id
    ).all()
    return generate_heatmap_data(topics)


@router.get("/material-topics")
def list_material_topics(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _get_project_or_404(db, project_id, current_user)
    topics = get_material_topics(db, project_id)
    return [_topic_to_dict(t) for t in topics]


@router.post("/complete")
def mark_complete(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    project = _get_project_or_404(db, project_id, current_user)
    topics = db.query(MaterialityTopic).filter(
        MaterialityTopic.project_id == project_id
    ).all()

    material_count = sum(1 for t in topics if t.is_material)
    project.materiality_complete = True
    db.commit()

    return {
        "status": "completed",
        "total_topics": len(topics),
        "material_topics": material_count,
    }


def _get_project_or_404(db, project_id, user) -> Project:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(404, "Project not found")
    if str(project.owner_id) != str(user.id):
        raise HTTPException(403, "Access denied")
    return project


def _topic_to_dict(t: MaterialityTopic) -> dict:
    return {
        "id": str(t.id),
        "esrs_standard": t.esrs_standard,
        "esrs_topic": t.esrs_topic,
        "esrs_sub_topic": t.esrs_sub_topic,
        "impact_scale": t.impact_scale,
        "impact_scope": t.impact_scope,
        "impact_irremediability": t.impact_irremediability,
        "impact_likelihood": t.impact_likelihood,
        "impact_score": t.impact_score,
        "financial_magnitude": t.financial_magnitude,
        "financial_likelihood": t.financial_likelihood,
        "financial_score": t.financial_score,
        "is_material": t.is_material,
        "is_positive_impact": t.is_positive_impact,
        "time_horizon": t.time_horizon,
        "materiality_rationale": t.materiality_rationale,
    }
