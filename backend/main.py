"""
CSRD-Agent API
End-to-end CSRD/ESRS SaaS Platform
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
import logging

from config import settings
from database import Base, engine

# Import all models so they are registered with SQLAlchemy
import models  # noqa: F401

# Import routers
from routes import auth, projects, emissions, materiality, iro, scenario, reports, data_collection, company, agent

# ─── Logging ────────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("csrd-agent")

# ─── App ────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="CSRD-Agent API",
    description=(
        "End-to-end CSRD/ESRS SaaS Platform for corporate sustainability reporting. "
        "Supports ESRS E1-E5, S1-S4, G1 with AI-generated narratives, GHG calculations, "
        "Double Materiality Assessment, IRO analysis, NGFS scenario analysis, and XBRL export."
    ),
    version=settings.APP_VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# ─── Create tables on startup ───────────────────────────────────────────────
@app.on_event("startup")
def create_tables():
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created/verified")
    except Exception as e:
        logger.error(f"Database init failed: {e}")

# ─── Middleware ──────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(round(process_time * 1000, 2))
    return response


# ─── Routers ────────────────────────────────────────────────────────────────
app.include_router(auth.router, prefix="/api")
app.include_router(projects.router, prefix="/api")
app.include_router(company.router, prefix="/api")
app.include_router(data_collection.router, prefix="/api")
app.include_router(emissions.router, prefix="/api")
app.include_router(materiality.router, prefix="/api")
app.include_router(iro.router, prefix="/api")
app.include_router(scenario.router, prefix="/api")
app.include_router(reports.router, prefix="/api")
app.include_router(agent.router, prefix="/api")

# ─── Health Check ───────────────────────────────────────────────────────────
@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "service": "CSRD-Agent API",
    }


@app.get("/api/debug/db")
def debug_db():
    """Database connectivity check — useful for diagnosing deployment issues."""
    from sqlalchemy import text, inspect as sa_inspect
    from database import engine as db_engine
    try:
        with db_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        inspector = sa_inspect(db_engine)
        tables = inspector.get_table_names()
        return {"status": "connected", "tables": tables, "table_count": len(tables)}
    except Exception as e:
        return {"status": "error", "detail": str(e)}


@app.get("/api/esrs-standards")
def list_esrs_standards():
    """List all ESRS 2025 standards."""
    from esrs_engine.mapping import get_esrs_structure
    structure = get_esrs_structure()
    return [
        {
            "id": k,
            "name": v["name"],
            "category": v["category"],
            "disclosure_count": len(v.get("disclosures", {})),
        }
        for k, v in structure.items()
    ]


# ─── Exception Handlers ─────────────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "type": type(exc).__name__},
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
