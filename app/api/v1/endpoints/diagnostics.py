"""Diagnostics endpoints for system checks."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.core.config.settings import settings

router = APIRouter()


@router.get("/diagnostics")
async def run_diagnostics(db: AsyncSession = Depends(get_db)) -> dict[str, Any]:
    """Run a series of lightweight diagnostics.

    Returns a JSON object indicating whether the database connection, OpenAI
    configuration, and CrewAI library are operational.
    """
    # Database connectivity -------------------------------------------------
    db_ok = False
    try:
        await db.execute(text("SELECT 1"))
        db_ok = True
    except Exception as exc:  # pragma: no cover – diagnostics only
        db_error = str(exc)
    else:
        db_error = None

    # OpenAI / LangChain integration ----------------------------------------
    openai_ok = False
    try:
        from langchain_openai import ChatOpenAI  # noqa: WPS433 – runtime import

        # Instantiation is cheap and does not perform a network call.
        _ = ChatOpenAI(api_key=settings.OPENAI_API_KEY, model="gpt-3.5-turbo")
        openai_ok = True
    except Exception as exc:  # pragma: no cover – diagnostics only
        openai_error = str(exc)
    else:
        openai_error = None

    # CrewAI library ---------------------------------------------------------
    crewai_ok = False
    try:
        import crewai  # noqa: WPS433 – runtime import

        # Simple version access to ensure import success
        _ = crewai.__version__  # type: ignore[attr-defined]
        crewai_ok = True
    except Exception as exc:  # pragma: no cover – diagnostics only
        crewai_error = str(exc)
    else:
        crewai_error = None

    # Aggregate results ------------------------------------------------------
    passed = db_ok and openai_ok and crewai_ok

    return {
        "overall_status": "ok" if passed else "failed",
        "database": {"ok": db_ok, "error": db_error},
        "openai": {"ok": openai_ok, "error": openai_error},
        "crewai": {"ok": crewai_ok, "error": crewai_error},
    } 