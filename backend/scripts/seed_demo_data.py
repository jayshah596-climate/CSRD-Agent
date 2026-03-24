"""
Seed script – creates demo company, user, and sample CSRD data.
Run: python scripts/seed_demo_data.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal, Base, engine
import models  # noqa
from models.user import User, UserRole, SubscriptionTier
from models.company import Company
from models.project import Project, ProjectStatus
from models.emissions import EmissionEntry, EmissionScope, EmissionFactor
from models.materiality import MaterialityTopic
from models.iro import IRO, IROType, IRORisk
from services.auth_service import get_password_hash
from services.materiality_service import (
    calculate_impact_score, calculate_financial_score, is_material
)
from services.iro_service import calculate_iro_score
import uuid
from datetime import datetime

Base.metadata.create_all(bind=engine)

db = SessionLocal()

print("🌱 Seeding demo data…")

# ─── Company ────────────────────────────────────────────────────────────────
company = db.query(Company).filter(Company.name == "Acme Industrials GmbH").first()
if not company:
    company = Company(
        id=uuid.uuid4(),
        name="Acme Industrials GmbH",
        legal_name="Acme Industrials GmbH & Co. KG",
        lei_code="5493001KJTIIGC8Y1R12",
        nace_code="C29.1",
        sector="Automotive",
        sub_sector="Motor vehicle manufacturing",
        employee_count=8450,
        annual_revenue=1250.5,
        total_assets=3200.0,
        country="Germany",
        headquarters_address="Musterstraße 1, 80331 München, Germany",
        reporting_year=2024,
        website="https://acme-industrials.example.com",
        sustainability_contact_email="sustainability@acme-industrials.example.com",
    )
    db.add(company)
    db.flush()
    print(f"  ✓ Company: {company.name}")

# ─── Admin User ─────────────────────────────────────────────────────────────
admin = db.query(User).filter(User.email == "demo@csrdagent.eu").first()
if not admin:
    admin = User(
        id=uuid.uuid4(),
        email="demo@csrdagent.eu",
        hashed_password=get_password_hash("Demo@2024!"),
        full_name="Demo User",
        role=UserRole.ADMIN,
        subscription_tier=SubscriptionTier.ENTERPRISE,
        company_id=company.id,
        is_active=True,
        is_verified=True,
    )
    db.add(admin)
    db.flush()
    print(f"  ✓ User: {admin.email} / Demo@2024!")

# ─── Project ─────────────────────────────────────────────────────────────
project = db.query(Project).filter(
    Project.name == "CSRD Report FY 2024 – Acme Industrials"
).first()
if not project:
    project = Project(
        id=uuid.uuid4(),
        name="CSRD Report FY 2024 – Acme Industrials",
        description="ESRS 2025 compliance report for fiscal year 2024",
        reporting_year=2024,
        company_id=company.id,
        owner_id=admin.id,
        esrs_standards=["E1", "E2", "E3", "S1", "G1"],
        status=ProjectStatus.IN_PROGRESS,
        data_collection_complete=True,
        materiality_complete=True,
        emissions_complete=True,
    )
    db.add(project)
    db.flush()
    print(f"  ✓ Project: {project.name}")

# ─── GHG Emissions ────────────────────────────────────────────────────────
emission_data = [
    # Scope 1
    (EmissionScope.SCOPE_1, "Natural gas – manufacturing", 12500000, "m3", 2.034, "kgCO2e/m3", "DEFRA 2023", None),
    (EmissionScope.SCOPE_1, "Diesel – company fleet", 450000, "litre", 2.687, "kgCO2e/litre", "DEFRA 2023", None),
    (EmissionScope.SCOPE_1, "Refrigerant leakage (HFC-134a)", 850, "kg", 1430.0, "kgCO2e/kg", "IPCC AR6", None),
    # Scope 2
    (EmissionScope.SCOPE_2_LOCATION, "Electricity – all sites", 85000000, "kWh", 0.276, "kgCO2e/kWh", "EEA 2023", None),
    (EmissionScope.SCOPE_2_MARKET, "Electricity – market (PPAs)", 85000000, "kWh", 0.048, "kgCO2e/kWh", "Supplier certificates", None),
    # Scope 3
    (EmissionScope.SCOPE_3, "Steel – purchased goods", 45000, "tonne", 2100.0, "kgCO2e/tonne", "IPCC 2023", "cat1"),
    (EmissionScope.SCOPE_3, "Aluminum – purchased goods", 8500, "tonne", 11500.0, "kgCO2e/tonne", "IPCC 2023", "cat1"),
    (EmissionScope.SCOPE_3, "Business travel – flights", 2800000, "km", 0.225, "kgCO2e/km/pax", "DEFRA 2023", "cat6"),
    (EmissionScope.SCOPE_3, "Employee commuting", 120000000, "km", 0.170, "kgCO2e/km", "DEFRA 2023", "cat7"),
    (EmissionScope.SCOPE_3, "Logistics – upstream transport", 18500000, "km", 0.092, "kgCO2e/tonne-km", "DEFRA 2023", "cat4"),
    (EmissionScope.SCOPE_3, "Use of sold products – vehicles", 15000, "tonne", 2500.0, "kgCO2e/unit/yr", "VDA 2023", "cat11"),
]

existing_emissions = db.query(EmissionEntry).filter(EmissionEntry.project_id == project.id).count()
if existing_emissions == 0:
    for scope, source, activity, unit, ef, ef_unit, ef_src, category in emission_data:
        co2e = round(activity * ef / 1000.0, 2)
        entry = EmissionEntry(
            project_id=project.id,
            company_id=company.id,
            scope=scope,
            source_name=source,
            activity_value=activity,
            activity_unit=unit,
            emission_factor_value=ef,
            emission_factor_unit=ef_unit,
            emission_factor_source=ef_src,
            co2e_tonnes=co2e,
            reporting_year=2024,
            category=category,
        )
        db.add(entry)
    print(f"  ✓ Emission entries: {len(emission_data)} entries added")

# ─── Materiality Topics ───────────────────────────────────────────────────
topic_data = [
    ("E1", "Climate change", 4.5, 4.2, 4.8, 4.0, 4.5, 4.3),
    ("E2", "Pollution", 3.0, 3.5, 3.2, 3.5, 2.8, 3.0),
    ("E3", "Water and marine resources", 2.5, 2.8, 2.0, 3.0, 2.2, 2.5),
    ("E4", "Biodiversity and ecosystems", 2.0, 2.2, 1.8, 2.5, 1.8, 2.0),
    ("E5", "Resource use and circular economy", 3.5, 3.8, 3.0, 4.0, 3.5, 3.8),
    ("S1", "Own workforce", 3.8, 4.0, 3.5, 4.5, 4.0, 4.2),
    ("S2", "Workers in the value chain", 3.2, 3.5, 3.0, 3.8, 3.0, 3.2),
    ("S3", "Affected communities", 2.5, 2.8, 2.2, 3.0, 2.0, 2.5),
    ("S4", "Consumers and end-users", 3.0, 3.2, 2.8, 3.5, 2.5, 3.0),
    ("G1", "Business conduct", 3.5, 3.8, 3.2, 4.0, 3.8, 4.0),
]

existing_topics = db.query(MaterialityTopic).filter(MaterialityTopic.project_id == project.id).count()
if existing_topics == 0:
    for std, topic, i_scale, i_scope, i_irr, i_like, f_mag, f_like in topic_data:
        i_score = calculate_impact_score(i_scale, i_scope, i_irr, i_like, is_negative=True)
        f_score = calculate_financial_score(f_mag, f_like)
        material = is_material(i_score, f_score)
        t = MaterialityTopic(
            project_id=project.id,
            company_id=company.id,
            esrs_standard=std,
            esrs_topic=topic,
            impact_scale=i_scale,
            impact_scope=i_scope,
            impact_irremediability=i_irr,
            impact_likelihood=i_like,
            impact_score=i_score,
            financial_magnitude=f_mag,
            financial_likelihood=f_like,
            financial_score=f_score,
            is_material=material,
        )
        db.add(t)
    print(f"  ✓ Materiality topics: {len(topic_data)} topics assessed")

# ─── IROs ─────────────────────────────────────────────────────────────────
iro_data = [
    {
        "iro_type": IROType.RISK,
        "risk_type": IRORisk.PHYSICAL_CHRONIC,
        "title": "Chronic temperature increase – cooling costs and productivity",
        "description": "Rising average temperatures increase energy costs for cooling manufacturing facilities and reduce worker productivity in warmer months.",
        "esrs_standard": "E1",
        "likelihood_score": 4.0,
        "magnitude_score": 3.5,
        "velocity_score": 2.5,
        "financial_impact_min": 5.0,
        "financial_impact_max": 15.0,
        "time_horizon": "medium",
        "is_climate_related": True,
    },
    {
        "iro_type": IROType.RISK,
        "risk_type": IRORisk.TRANSITION_POLICY,
        "title": "EU ETS carbon price escalation",
        "description": "Increasing EU ETS carbon prices will significantly raise operational costs for Scope 1 emitting activities.",
        "esrs_standard": "E1",
        "likelihood_score": 4.5,
        "magnitude_score": 4.0,
        "velocity_score": 3.5,
        "financial_impact_min": 12.0,
        "financial_impact_max": 45.0,
        "time_horizon": "short",
        "is_climate_related": True,
    },
    {
        "iro_type": IROType.OPPORTUNITY,
        "risk_type": None,
        "title": "EV drivetrain manufacturing transition",
        "description": "Significant market opportunity as automotive sector transitions to electric vehicles. Early investment in EV-related manufacturing lines.",
        "esrs_standard": "E1",
        "likelihood_score": 4.0,
        "magnitude_score": 4.5,
        "velocity_score": 4.0,
        "financial_impact_min": 50.0,
        "financial_impact_max": 200.0,
        "time_horizon": "medium",
        "is_climate_related": True,
    },
    {
        "iro_type": IROType.IMPACT,
        "risk_type": None,
        "title": "GHG emissions – climate change contribution",
        "description": "Operations contribute approximately 3.8 MtCO2e annually, contributing to global temperature increases.",
        "esrs_standard": "E1",
        "likelihood_score": 5.0,
        "magnitude_score": 4.0,
        "velocity_score": 3.0,
        "financial_impact_min": None,
        "financial_impact_max": None,
        "time_horizon": "long",
        "is_climate_related": True,
    },
]

existing_iros = db.query(IRO).filter(IRO.project_id == project.id).count()
if existing_iros == 0:
    for iro_dict in iro_data:
        score = calculate_iro_score(
            iro_dict["likelihood_score"],
            iro_dict["magnitude_score"],
            iro_dict.get("velocity_score", 3.0),
        )
        iro = IRO(
            project_id=project.id,
            company_id=company.id,
            overall_score=score,
            is_material=score >= 50,
            **iro_dict,
        )
        db.add(iro)
    print(f"  ✓ IROs: {len(iro_data)} entries added")

db.commit()
db.close()

print("\n✅ Demo data seeded successfully!")
print("─" * 40)
print("Demo credentials:")
print("  Email:    demo@csrdagent.eu")
print("  Password: Demo@2024!")
print("─" * 40)
