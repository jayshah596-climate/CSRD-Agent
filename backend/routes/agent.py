"""
CSRD Agent Route
POST /api/agent/analyze — streams the 8-step CSRD analysis via Server-Sent Events
"""

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
import logging

from services.csrd_agent_service import stream_csrd_analysis, run_csrd_analysis_sync

logger = logging.getLogger("csrd-agent")

router = APIRouter(prefix="/agent", tags=["agent"])


# ─── Request model ────────────────────────────────────────────────────────────

class AgentRequest(BaseModel):
    company_data: Dict[str, Any] = Field(
        ...,
        description="Company information including name, employees, revenue, country, etc.",
        example={
            "name": "Acme GmbH",
            "employees": 500,
            "revenue_eur_m": 120,
            "country": "Germany",
            "fiscal_year": 2024,
            "company_type": "Large EU",
            "subject_to_nfrd": False,
            "sector": "Manufacturing",
            "nace_code": "C25",
        },
    )
    reporting_requirements: List[str] = Field(
        ...,
        description="List of ESRS modules selected for reporting (e.g. ['E1', 'S1', 'G1'])",
        example=["E1", "S1", "G1"],
    )
    raw_data: Optional[str] = Field(
        default="",
        description="Raw sustainability data or metrics provided by the user",
        example="Scope 1: 1200 tCO2e, Scope 2: 800 tCO2e, Employees: 500, Women in leadership: 38%",
    )


# ─── Streaming endpoint ───────────────────────────────────────────────────────

@router.post(
    "/analyze",
    summary="Run CSRD end-to-end analysis (streaming)",
    response_description="Server-Sent Events stream of Claude's CSRD analysis",
)
async def analyze(request: AgentRequest):
    """
    Accepts company data, reporting requirements, and raw sustainability data,
    then streams Claude's comprehensive 8-step CSRD analysis as Server-Sent Events.

    Each SSE chunk is formatted as:  data: <text>\\n\\n
    A final  data: [DONE]\\n\\n  signals completion.
    Error chunks start with:  data: [ERROR] <message>\\n\\n
    """
    from config import settings

    api_key: Optional[str] = getattr(settings, "ANTHROPIC_API_KEY", None)

    async def generator():
        async for chunk in stream_csrd_analysis(
            company_data=request.company_data,
            reporting_requirements=request.reporting_requirements,
            raw_data=request.raw_data or "",
            api_key=api_key,
        ):
            yield chunk

    return StreamingResponse(
        generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


# ─── Synchronous endpoint (Vercel-compatible) ─────────────────────────────────

@router.post(
    "/analyze-sync",
    summary="Run CSRD end-to-end analysis (synchronous JSON response)",
    response_description="Complete 8-step CSRD analysis returned as JSON once finished",
)
async def analyze_sync(request: AgentRequest):
    """
    Vercel-compatible synchronous endpoint.

    Runs the full 8-step CSRD analysis via a single blocking Claude call
    (max_tokens=4000, ~25-35 seconds) and returns all sections as JSON.
    Use this instead of /analyze on serverless deployments (Vercel, Lambda).

    Response shape:
      {
        "sections": {
          "wave_eligibility": "...",
          "esrs_modules": "...",
          "data_processing": "...",
          "double_materiality": "...",
          "iro_analysis": "...",
          "climate_scenario": "...",
          "esg_report": "...",
          "xbrl_specifications": "..."
        },
        "full_text": "...",
        "usage": { "input_tokens": N, "output_tokens": N }
      }
    """
    import asyncio
    from fastapi import HTTPException

    from config import settings
    api_key: Optional[str] = getattr(settings, "ANTHROPIC_API_KEY", None)

    if not api_key:
        raise HTTPException(status_code=503, detail="ANTHROPIC_API_KEY not configured.")

    try:
        result = await asyncio.to_thread(
            run_csrd_analysis_sync,
            request.company_data,
            request.reporting_requirements,
            request.raw_data or "",
            api_key,
        )
        return result
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
