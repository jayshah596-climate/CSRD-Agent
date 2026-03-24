import enum
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, Float, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from database import Base


class IROType(str, enum.Enum):
    IMPACT = "impact"
    RISK = "risk"
    OPPORTUNITY = "opportunity"


class IRORisk(str, enum.Enum):
    PHYSICAL_ACUTE = "physical_acute"
    PHYSICAL_CHRONIC = "physical_chronic"
    TRANSITION_POLICY = "transition_policy"
    TRANSITION_TECHNOLOGY = "transition_technology"
    TRANSITION_MARKET = "transition_market"
    TRANSITION_REPUTATIONAL = "transition_reputational"
    SYSTEMIC = "systemic"


class IRO(Base):
    __tablename__ = "iros"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)

    iro_type = Column(Enum(IROType), nullable=False)
    risk_type = Column(Enum(IRORisk), nullable=True)

    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)

    # ESRS link
    esrs_standard = Column(String(10), nullable=True)
    esrs_topic = Column(String(255), nullable=True)

    # Scoring
    likelihood_score = Column(Float, nullable=True)  # 1-5
    magnitude_score = Column(Float, nullable=True)  # 1-5
    velocity_score = Column(Float, nullable=True)  # 1-5 (speed of onset)
    overall_score = Column(Float, nullable=True)

    # Financial impact
    financial_impact_min = Column(Float, nullable=True)  # EUR millions
    financial_impact_max = Column(Float, nullable=True)  # EUR millions
    financial_impact_currency = Column(String(10), default="EUR")

    # Time horizon
    time_horizon = Column(String(20), nullable=True)  # short (0-3yr), medium (3-10yr), long (10+yr)

    # Response
    current_controls = Column(Text, nullable=True)
    management_approach = Column(Text, nullable=True)
    target_metric = Column(String(255), nullable=True)

    is_material = Column(Boolean, default=False)
    is_climate_related = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="iros")
