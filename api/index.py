import sys
import os

# Add backend directory to Python path so all backend modules are importable
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend'))
sys.path.insert(0, backend_path)

from main import app  # noqa: F401 — Vercel uses this `app` as the ASGI handler
