"""
main.py
-------
FastAPI application entry point for the Global Social Media Activity Map
data ingestion service (Coriolis).

Startup
-------
Run with:
    uvicorn main:app --reload --host 0.0.0.0 --port 8000

Endpoints
---------
GET  /health        — liveness probe
POST /ingest/gdelt  — manual GDELT GKG pull (returns sample rows)
"""

from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

import os
import uvicorn
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from database.models import create_tables
from ingestion.gdelt_client import fetch_latest_gkg
from ingestion.gdelt_client import gkg_row_to_activity
from ingestion.mastodon_client import stream_public

from api.main import api_router

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Background tasks
# ---------------------------------------------------------------------------
_mastodon_task: asyncio.Task | None = None


async def _run_mastodon_stream() -> None:
    """Run the Mastodon public stream in a thread so it doesn't block the loop."""
    def _store(record: dict) -> None:
        logger.info("[mastodon] %s", record.get("text", "")[:80])

    await asyncio.to_thread(stream_public, _store)


# ---------------------------------------------------------------------------
# Lifespan
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: ANN201
    """
    Application startup/shutdown.

    On startup:
      - Ensure DB tables exist (idempotent).
      - Launch the Mastodon stream listener as a background task.
    """
    global _mastodon_task

    logger.info("Coriolis starting up — creating DB tables if absent…")
    try:
        create_tables()
        logger.info("DB tables ready.")
    except Exception as exc:
        logger.warning("Could not create DB tables (is PostgreSQL running?): %s", exc)

    # Launch Mastodon stream
    _mastodon_task = asyncio.create_task(_run_mastodon_stream())
    logger.info("Mastodon stream task launched.")

    yield

    # Shutdown
    if _mastodon_task and not _mastodon_task.done():
        _mastodon_task.cancel()
        logger.info("Mastodon stream task cancelled.")


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Coriolis — Global Social Media Activity Map",
    description=(
        "Data ingestion API that aggregates real-time social signals from "
        "Mastodon and geopolitical events from GDELT GKG."
    ),
    version="0.1.0",
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------
_raw_origins = os.getenv("ALLOWED_ORIGINS", "*")
allowed_origins: list[str] = (
    ["*"] if _raw_origins == "*" else [o.strip() for o in _raw_origins.split(",")]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

app.include_router(api_router)

_FRONTEND = Path(__file__).parent / "frontend"


@app.get("/", include_in_schema=False)
async def root() -> FileResponse:
    """Serve the Coriolis frontend SPA."""
    return FileResponse(str(_FRONTEND / "index.html"))


@app.get("/health", tags=["ops"])
async def health() -> dict[str, str]:
    """Liveness probe — always returns 200 OK."""
    return {"status": "ok", "service": "coriolis"}


@app.post("/ingest/gdelt", tags=["ingestion"])
async def ingest_gdelt(
    background_tasks: BackgroundTasks,
    max_rows: int = 50,
) -> JSONResponse:
    """
    Manually trigger a GDELT GKG pull.

    Returns the first *max_rows* records converted to SocialActivity format.
    In production this endpoint would persist to PostgreSQL; here it
    returns the data directly for inspection.
    """
    def _pull() -> list[dict[str, Any]]:
        df = fetch_latest_gkg(max_rows=max_rows)
        return [gkg_row_to_activity(row) for _, row in df.iterrows()]

    records = await asyncio.to_thread(_pull)
    return JSONResponse(content={"count": len(records), "records": records})


# ---------------------------------------------------------------------------
# Static files — frontend SPA (must come AFTER all API routes)
# ---------------------------------------------------------------------------
if _FRONTEND.exists():
    app.mount("/static", StaticFiles(directory=str(_FRONTEND)), name="static")


# ---------------------------------------------------------------------------
# Dev entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
