import enum
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, Text, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from database import Base


class ReportStatus(str, enum.Enum):
    GENERATING = "generating"
    DRAFT = "draft"
    FINAL = "final"
    PUBLISHED = "published"
    FAILED = "failed"


class ReportFormat(str, enum.Enum):
    PDF = "pdf"
    EXCEL = "excel"
    JSON = "json"
    XBRL = "xbrl"
    WEB = "web"


class Report(Base):
    __tablename__ = "reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)

    title = Column(String(500), nullable=False)
    reporting_year = Column(Integer, nullable=False)
    status = Column(Enum(ReportStatus), default=ReportStatus.DRAFT)
    version = Column(Integer, default=1)

    # Content
    executive_summary = Column(Text, nullable=True)
    report_content = Column(JSONB, default=dict)  # Full structured ESRS content
    esrs_disclosures = Column(JSONB, default=dict)  # ESRS-mapped disclosures
    kpis = Column(JSONB, default=dict)

    # Exports
    pdf_url = Column(String(500), nullable=True)
    excel_url = Column(String(500), nullable=True)
    xbrl_url = Column(String(500), nullable=True)
    json_url = Column(String(500), nullable=True)
    web_url = Column(String(500), nullable=True)

    # Access control
    is_public = Column(String(10), default="private")
    access_token = Column(String(255), nullable=True)

    # Generation metadata
    generation_log = Column(JSONB, default=list)
    ai_model_used = Column(String(100), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime, nullable=True)

    # Relationships
    project = relationship("Project", back_populates="reports")

    def __repr__(self):
        return f"<Report {self.title} v{self.version}>"
