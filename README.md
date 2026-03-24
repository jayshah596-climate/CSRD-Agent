# CSRD-Agent – End-to-End ESRS 2025 SaaS Platform

A production-ready SaaS platform for **Corporate Sustainability Reporting Directive (CSRD)** compliance, built with **FastAPI + React + PostgreSQL**.

## Features

| Module | Description |
|---|---|
| **Data Collection** | Manual entry + file upload for all ESRS 2025 datapoints |
| **Double Materiality** | Impact + financial scoring, heatmap visualisation (EFRAG DMA) |
| **GHG Emissions** | Scope 1, 2, 3 calculations (GHG Protocol aligned) |
| **IRO Analysis** | Impacts, Risks, Opportunities (TCFD / ESRS aligned) |
| **Climate Scenarios** | NGFS Phase 4 scenarios, carbon cost, Value at Risk |
| **AI Narratives** | Claude-powered ESRS-compliant disclosures |
| **Report Generation** | PDF, Excel, JSON, XBRL multi-format export |
| **XBRL Filing** | ESRS XBRL taxonomy tagging for digital filing |
| **Multi-tenant SaaS** | JWT auth, role-based access, subscription tiers |

---

## Quick Start (Docker)

```bash
# Clone the repository
git clone https://github.com/jayshah596-climate/csrd-agent.git
cd csrd-agent

# Copy and configure environment
cp backend/.env.example backend/.env
# Edit backend/.env with your API keys

# Start all services
docker compose up -d

# Seed demo data
docker compose exec backend python scripts/seed_demo_data.py

# Access the platform
open http://localhost:80
```

**Demo credentials:**
- Email: `demo@csrdagent.eu`
- Password: `Demo@2024!`

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   React Frontend (port 80)               │
│     Tailwind CSS · React Query · Recharts · Zustand     │
└────────────────────────┬────────────────────────────────┘
                         │ HTTP/REST
┌────────────────────────▼────────────────────────────────┐
│              FastAPI Backend (port 8000)                 │
│                                                         │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│  │   Auth   │ │ Projects │ │Emissions │ │Materiality│  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘  │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│  │    IRO   │ │Scenarios │ │ Reports  │ │   XBRL   │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘  │
│                                                         │
│  ┌────────────────────┐  ┌─────────────────────────┐   │
│  │   ESRS Engine      │  │   AI Narrative Service  │   │
│  │  E1-E5, S1-S4, G1  │  │   (Claude / Templates)  │   │
│  └────────────────────┘  └─────────────────────────┘   │
└────────────────┬──────────────────────────┬────────────┘
                 │                          │
┌────────────────▼──────┐      ┌────────────▼────────────┐
│   PostgreSQL 15        │      │      Redis 7            │
│  (all persistent data) │      │  (cache / task queue)   │
└───────────────────────┘      └─────────────────────────┘
```

---

## Development Setup

### Backend

```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Set up PostgreSQL locally
createdb csrd_db
createuser csrd_user
psql -c "ALTER USER csrd_user WITH PASSWORD 'csrd_password';"
psql -c "GRANT ALL ON DATABASE csrd_db TO csrd_user;"

# Configure environment
cp .env.example .env
# Edit .env as needed

# Run migrations
alembic upgrade head

# Seed demo data
python scripts/seed_demo_data.py

# Start dev server
uvicorn main:app --reload --port 8000
```

API docs available at: `http://localhost:8000/api/docs`

### Frontend

```bash
cd frontend
npm install
npm start   # starts on http://localhost:3000
```

---

## Running Tests

```bash
cd backend
pip install pytest pytest-asyncio httpx
pytest tests/ -v
```

---

## Environment Variables

| Variable | Description | Required |
|---|---|---|
| `DATABASE_URL` | PostgreSQL connection string | ✅ |
| `SECRET_KEY` | JWT signing key (min 32 chars) | ✅ |
| `ANTHROPIC_API_KEY` | Claude API key for AI narratives | Optional |
| `STRIPE_SECRET_KEY` | Stripe for subscription billing | Optional |
| `REDIS_URL` | Redis for caching/tasks | Optional |

---

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/auth/register` | Create account |
| `POST` | `/api/auth/login` | Login (OAuth2) |
| `GET` | `/api/auth/me` | Current user |
| `GET/POST` | `/api/projects` | List / create projects |
| `GET` | `/api/projects/{id}/progress` | Workflow progress |
| `GET/POST` | `/api/projects/{id}/emissions` | GHG entries |
| `GET` | `/api/projects/{id}/emissions/summary` | Scope totals |
| `GET/PUT` | `/api/projects/{id}/materiality/topics` | DMA scoring |
| `GET` | `/api/projects/{id}/materiality/heatmap` | Matrix data |
| `GET/POST` | `/api/projects/{id}/iro` | IRO entries |
| `GET` | `/api/projects/{id}/iro/summary` | Risk summary |
| `POST` | `/api/projects/{id}/scenarios/run` | NGFS analysis |
| `POST` | `/api/projects/{id}/reports/generate` | Generate report |
| `GET` | `/api/projects/{id}/reports/{rid}/download/{fmt}` | Download |

Full interactive docs: `http://localhost:8000/api/docs`

---

## ESRS 2025 Coverage

| Standard | Name | Disclosures |
|---|---|---|
| ESRS 2 | General Disclosures | GOV-1–5, SBM-1–3, IRO-1–2, MDR-P/A/T |
| E1 | Climate Change | E1-1 through E1-9 |
| E2 | Pollution | E2-1 through E2-6 |
| E3 | Water & Marine | E3-1 through E3-5 |
| E4 | Biodiversity | E4-1 through E4-6 |
| E5 | Circular Economy | E5-1 through E5-6 |
| S1 | Own Workforce | S1-1 through S1-17 |
| S2 | Value Chain Workers | S2-1 through S2-5 |
| S3 | Affected Communities | S3-1 through S3-5 |
| S4 | Consumers | S4-1 through S4-5 |
| G1 | Business Conduct | G1-1 through G1-6 |

---

## XBRL Output

Generated XBRL instance documents conform to:
- **EFRAG ESRS XBRL Taxonomy 2024**
- Namespace: `https://xbrl.efrag.org/taxonomy/esrs/2024`
- iXBRL inline tagging for web reports
- Key facts tagged: GHG emissions, energy, workforce, governance KPIs

---

## Subscription Plans

| Plan | Features |
|---|---|
| **Free** | 1 project, basic data entry, JSON export |
| **Pro** | 5 projects, AI narratives, PDF/Excel/XBRL export |
| **Enterprise** | Unlimited projects, all features, API access, audit trail |

---

## Tech Stack

**Backend:** Python 3.11 · FastAPI · SQLAlchemy 2 · Alembic · PostgreSQL 15 · Pydantic v2
**Frontend:** React 18 · Tailwind CSS 3 · React Query · Recharts · Zustand
**AI:** Anthropic Claude (narrative generation)
**Export:** ReportLab (PDF) · openpyxl (Excel) · lxml (XBRL)
**Infrastructure:** Docker · Nginx · Redis · Celery

---

## License

MIT License – see LICENSE file.

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit changes: `git commit -m "feat: add my feature"`
4. Push and open a Pull Request

---

*Built with ❤️ for CSRD compliance – ESRS 2025 ready*
