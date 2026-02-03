import shutil
import logging
from pathlib import Path
from datetime import datetime, timezone, timedelta

from app.config import UPLOADS_DIR, EXPORTS_DIR, FILE_RETENTION_HOURS

logger = logging.getLogger(__name__)


def cleanup_old_files():
    """Remove files older than FILE_RETENTION_HOURS."""
    cutoff = datetime.now(timezone.utc) - timedelta(hours=FILE_RETENTION_HOURS)

    for directory in [UPLOADS_DIR, EXPORTS_DIR]:
        if not directory.exists():
            continue
        for item in directory.iterdir():
            try:
                mtime = datetime.fromtimestamp(item.stat().st_mtime, tz=timezone.utc)
                if mtime < cutoff:
                    if item.is_dir():
                        shutil.rmtree(item)
                    else:
                        item.unlink()
                    logger.info("Cleaned up old file: %s", item)
            except OSError as e:
                logger.warning("Failed to clean up %s: %s", item, e)


def get_disk_usage(directory: Path) -> int:
    """Get total size of a directory in bytes."""
    total = 0
    if directory.exists():
        for item in directory.rglob("*"):
            if item.is_file():
                total += item.stat().st_size
    return total
