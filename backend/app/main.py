"""
main.py
-------
FastAPI application entry point.

Run with:
  uvicorn app.main:app --reload --port 5000
"""

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from app.database.db import init_db
from app.utils.storage_utils import ensure_storage_dir
from app.services.backup_scheduler import start_scheduler, stop_scheduler
from app.routes import upload, files, versions, restore

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# ── CORS origins ──────────────────────────────────────────────────────────────
ALLOWED_ORIGINS = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:3000,http://127.0.0.1:3000",
).split(",")


# ── Lifespan (startup / shutdown) ─────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up FileVault backend…")
    ensure_storage_dir()
    init_db()
    start_scheduler()
    yield
    logger.info("Shutting down…")
    stop_scheduler()


# ── App ────────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="FileVault API",
    description="File version-control system – upload, track, and restore files.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ── Middleware ─────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ────────────────────────────────────────────────────────────────────
app.include_router(upload.router)
app.include_router(files.router)
app.include_router(versions.router)
app.include_router(restore.router)


# ── Health check ───────────────────────────────────────────────────────────────
@app.get("/health", tags=["health"])
def health():
    return {"status": "ok", "service": "FileVault API"}


# ── Dev entry point ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=5000, reload=True)
