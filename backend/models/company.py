import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, Integer, Float
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from database import Base


class Company(Base):
    __tablename__ = "companies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    legal_name = Column(String(255), nullable=True)
    registration_number = Column(String(100), nullable=True)
    lei_code = Column(String(20), nullable=True)  # Legal Entity Identifier

    # Industry classification
    nace_code = Column(String(20), nullable=True)  # EU industry code
    sector = Column(String(100), nullable=True)
    sub_sector = Column(String(100), nullable=True)

    # Size
    employee_count = Column(Integer, nullable=True)
    annual_revenue = Column(Float, nullable=True)  # EUR millions
    total_assets = Column(Float, nullable=True)  # EUR millions

    # Geography
    country = Column(String(100), nullable=True)
    headquarters_address = Column(Text, nullable=True)
    operating_countries = Column(JSONB, default=list)

    # Reporting
    reporting_year = Column(Integer, nullable=True)
    fiscal_year_end = Column(String(10), nullable=True)  # MM-DD

    # Contact
    website = Column(String(255), nullable=True)
    sustainability_contact_email = Column(String(255), nullable=True)

    # Metadata
    logo_url = Column(String(500), nullable=True)
    settings = Column(JSONB, default=dict)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    users = relationship("User", back_populates="company")
    projects = relationship("Project", back_populates="company")

    def __repr__(self):
        return f"<Company {self.name}>"
