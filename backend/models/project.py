import enum
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Enum, ForeignKey, Text, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from database import Base


class ProjectStatus(str, enum.Enum):
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class Project(Base):
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    reporting_year = Column(Integer, nullable=False)
    status = Column(Enum(ProjectStatus), default=ProjectStatus.DRAFT)

    # Ownership
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # ESRS scope
    esrs_standards = Column(JSONB, default=list)  # ["E1", "E2", "S1", "G1", ...]
    reporting_boundary = Column(String(100), nullable=True)  # consolidation scope

    # Workflow progress
    data_collection_complete = Column(Boolean, default=False)
    materiality_complete = Column(Boolean, default=False)
    iro_complete = Column(Boolean, default=False)
    emissions_complete = Column(Boolean, default=False)
    scenario_complete = Column(Boolean, default=False)
    narrative_complete = Column(Boolean, default=False)

    # Settings
    settings = Column(JSONB, default=dict)
    metadata_ = Column("metadata", JSONB, default=dict)

    # Versioning
    version = Column(Integer, default=1)
    is_locked = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    company = relationship("Company", back_populates="projects")
    owner = relationship("User", back_populates="projects")
    reports = relationship("Report", back_populates="project")
    emissions = relationship("EmissionEntry", back_populates="project")
    materiality_topics = relationship("MaterialityTopic", back_populates="project")
    iros = relationship("IRO", back_populates="project")
    data_entries = relationship("DataCollectionEntry", back_populates="project")

    def __repr__(self):
        return f"<Project {self.name} ({self.reporting_year})>"
