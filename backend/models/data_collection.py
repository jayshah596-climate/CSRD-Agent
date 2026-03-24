import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Text, Float, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from database import Base


class DataCollectionEntry(Base):
    __tablename__ = "data_collection_entries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)

    # ESRS mapping
    esrs_standard = Column(String(10), nullable=False)  # E1, S1, G1...
    esrs_disclosure = Column(String(50), nullable=True)  # E1-1, E1-2...
    datapoint_id = Column(String(100), nullable=True)
    datapoint_name = Column(String(500), nullable=False)

    # Data
    data_type = Column(String(50), nullable=False)  # numeric, text, boolean, date
    value_numeric = Column(Float, nullable=True)
    value_text = Column(Text, nullable=True)
    value_boolean = Column(Boolean, nullable=True)
    unit = Column(String(50), nullable=True)

    # Source
    source_type = Column(String(50), nullable=True)  # manual, file_upload, api
    source_reference = Column(String(500), nullable=True)
    is_estimated = Column(Boolean, default=False)
    confidence_level = Column(String(20), nullable=True)  # high, medium, low

    # Validation
    is_validated = Column(Boolean, default=False)
    validated_by = Column(String(255), nullable=True)
    validation_notes = Column(Text, nullable=True)

    reporting_period = Column(String(50), nullable=True)
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="data_entries")


class ESRSDataPoint(Base):
    """Master reference table of all ESRS 2025 data points."""
    __tablename__ = "esrs_datapoints"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    esrs_standard = Column(String(10), nullable=False, index=True)
    disclosure_id = Column(String(50), nullable=False)  # E1-1, E1-2
    datapoint_id = Column(String(100), nullable=False, unique=True)
    datapoint_name = Column(String(500), nullable=False)
    datapoint_description = Column(Text, nullable=True)

    data_type = Column(String(50), nullable=False)
    unit = Column(String(50), nullable=True)
    is_mandatory = Column(Boolean, default=True)
    is_conditional = Column(Boolean, default=False)
    condition = Column(Text, nullable=True)

    esrs_paragraph = Column(String(50), nullable=True)
    xbrl_tag = Column(String(500), nullable=True)

    category = Column(String(50), nullable=True)  # E, S, G
    topic = Column(String(255), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
