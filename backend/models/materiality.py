import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Float, Boolean, Text, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from database import Base


class MaterialityTopic(Base):
    __tablename__ = "materiality_topics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)

    # ESRS standard reference
    esrs_standard = Column(String(10), nullable=False)  # E1, E2, S1, G1...
    esrs_topic = Column(String(255), nullable=False)
    esrs_sub_topic = Column(String(255), nullable=True)

    # Impact materiality
    impact_scale = Column(Float, nullable=True)  # 1-5
    impact_scope = Column(Float, nullable=True)  # 1-5
    impact_irremediability = Column(Float, nullable=True)  # 1-5
    impact_likelihood = Column(Float, nullable=True)  # 1-5
    impact_score = Column(Float, nullable=True)  # calculated

    # Financial materiality
    financial_magnitude = Column(Float, nullable=True)  # 1-5
    financial_likelihood = Column(Float, nullable=True)  # 1-5
    financial_score = Column(Float, nullable=True)  # calculated

    # Overall
    is_material = Column(Boolean, default=False)
    materiality_rationale = Column(Text, nullable=True)
    stakeholder_weights = Column(JSONB, default=dict)

    # Status
    is_positive_impact = Column(Boolean, default=False)
    is_negative_impact = Column(Boolean, default=True)
    time_horizon = Column(String(20), nullable=True)  # short, medium, long

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="materiality_topics")


class MaterialityAssessment(Base):
    __tablename__ = "materiality_assessments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False, unique=True)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)

    # Methodology
    methodology = Column(String(100), default="ESRS_DMA")
    stakeholder_groups = Column(JSONB, default=list)
    assessment_date = Column(DateTime, nullable=True)

    # Summary
    total_topics_assessed = Column(Integer, default=0)
    material_topics_count = Column(Integer, default=0)
    heatmap_data = Column(JSONB, default=dict)
    summary_narrative = Column(Text, nullable=True)

    # Status
    is_complete = Column(Boolean, default=False)
    reviewed_by = Column(String(255), nullable=True)
    approved_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
