"""
services/backup_scheduler.py
-----------------------------
APScheduler-based background jobs for automated backups.
Register the scheduler in main.py startup/shutdown events.
"""

import logging
import os
import shutil
from datetime import datetime
from pathlib import Path

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.utils.storage_utils import STORAGE_DIR

logger = logging.getLogger(__name__)

BACKUP_DIR = Path(os.getenv("BACKUP_DIR", "./backups"))
# Default: run backup every day at 02:00
BACKUP_CRON = os.getenv("BACKUP_CRON", "0 2 * * *")

_scheduler = BackgroundScheduler(timezone="UTC")


# ── Backup Job ────────────────────────────────────────────────────────────────

def _run_backup() -> None:
    """Copy the entire storage directory into a timestamped backup folder."""
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    dest = BACKUP_DIR / f"backup_{timestamp}"
    try:
        shutil.copytree(STORAGE_DIR, dest)
        logger.info("Backup completed → %s", dest)
        _prune_old_backups()
    except Exception as exc:
        logger.error("Backup failed: %s", exc)


def _prune_old_backups(keep: int = 7) -> None:
    """Remove oldest backups, keeping only the *keep* most recent."""
    if not BACKUP_DIR.exists():
        return
    backups = sorted(BACKUP_DIR.glob("backup_*"), key=lambda p: p.stat().st_mtime)
    for old in backups[:-keep]:
        shutil.rmtree(old, ignore_errors=True)
        logger.info("Pruned old backup: %s", old)


# ── Public API ────────────────────────────────────────────────────────────────

def start_scheduler() -> None:
    """Register jobs and start the scheduler (call from FastAPI startup)."""
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    hour, minute = _parse_cron(BACKUP_CRON)
    _scheduler.add_job(
        _run_backup,
        CronTrigger(hour=hour, minute=minute),
        id="daily_backup",
        replace_existing=True,
    )
    _scheduler.start()
    logger.info("Backup scheduler started (cron: %s)", BACKUP_CRON)


def stop_scheduler() -> None:
    """Gracefully shut down the scheduler (call from FastAPI shutdown)."""
    if _scheduler.running:
        _scheduler.shutdown(wait=False)
        logger.info("Backup scheduler stopped.")


def trigger_backup_now() -> str:
    """Immediately run a backup and return the destination path as a string."""
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    dest = BACKUP_DIR / f"backup_{timestamp}"
    shutil.copytree(STORAGE_DIR, dest)
    _prune_old_backups()
    return str(dest)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _parse_cron(cron_str: str) -> tuple[int, int]:
    """Parse 'M H * * *' → (hour, minute). Falls back to (2, 0) on error."""
    try:
        parts = cron_str.split()
        return int(parts[1]), int(parts[0])
    except Exception:
        return 2, 0
