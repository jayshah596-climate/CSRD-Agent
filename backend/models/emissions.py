import enum
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, Float, Integer, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from database import Base


class EmissionScope(str, enum.Enum):
    SCOPE_1 = "scope_1"
    SCOPE_2_LOCATION = "scope_2_location"
    SCOPE_2_MARKET = "scope_2_market"
    SCOPE_3 = "scope_3"


class EmissionEntry(Base):
    __tablename__ = "emission_entries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)

    scope = Column(Enum(EmissionScope), nullable=False)
    category = Column(String(100), nullable=True)  # e.g., Scope 3 cat 1-15
    source_name = Column(String(255), nullable=False)
    activity_description = Column(Text, nullable=True)

    # Activity data
    activity_value = Column(Float, nullable=False)
    activity_unit = Column(String(50), nullable=False)

    # Emission factor
    emission_factor_id = Column(UUID(as_uuid=True), ForeignKey("emission_factors.id"), nullable=True)
    emission_factor_value = Column(Float, nullable=True)
    emission_factor_unit = Column(String(100), nullable=True)
    emission_factor_source = Column(String(255), nullable=True)

    # Result
    co2e_tonnes = Column(Float, nullable=True)
    co2_tonnes = Column(Float, nullable=True)
    ch4_tonnes = Column(Float, nullable=True)
    n2o_tonnes = Column(Float, nullable=True)

    # Metadata
    reporting_year = Column(Integer, nullable=False)
    data_quality = Column(String(20), nullable=True)  # primary, secondary, estimated
    notes = Column(Text, nullable=True)
    source_document = Column(String(500), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="emissions")
    emission_factor = relationship("EmissionFactor")


class EmissionFactor(Base):
    __tablename__ = "emission_factors"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=False)
    sub_category = Column(String(100), nullable=True)

    # Factor values (kgCO2e per unit)
    factor_value = Column(Float, nullable=False)
    factor_unit = Column(String(100), nullable=False)
    co2_factor = Column(Float, nullable=True)
    ch4_factor = Column(Float, nullable=True)
    n2o_factor = Column(Float, nullable=True)

    # Source
    source = Column(String(255), nullable=False)
    source_year = Column(Integer, nullable=True)
    geography = Column(String(100), nullable=True)
    sector = Column(String(100), nullable=True)

    is_active = Column(String(10), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<EmissionFactor {self.name}: {self.factor_value} {self.factor_unit}>"
