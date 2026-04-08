from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from config import settings


def _ensure_ssl(url: str) -> str:
    """
    Auto-append sslmode=require for cloud PostgreSQL providers (Neon, Supabase,
    Render, Railway, etc.). Local connections are left unchanged.
    """
    if not url:
        return url
    if "localhost" in url or "127.0.0.1" in url:
        return url
    if "sslmode" in url:
        return url  # already configured
    sep = "&" if "?" in url else "?"
    return url + sep + "sslmode=require"


# NullPool is required for serverless (Vercel/Neon) — no persistent connections
engine = create_engine(
    _ensure_ssl(settings.DATABASE_URL),
    poolclass=NullPool,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
