import logging
import os
import time

from app import config

logger = logging.getLogger(__name__)


def cleanup_old_files() -> dict:
    threshold = time.time() - config.FILE_RETENTION_HOURS * 3600
    removed = {"audiobooks": [], "tmp": []}

    for dir_name, dir_path in [("audiobooks", config.AUDIOBOOKS_DIR), ("tmp", config.TMP_DIR)]:
        if not os.path.isdir(dir_path):
            continue
        for root, dirs, files in os.walk(dir_path, topdown=False):
            for fname in files:
                fpath = os.path.join(root, fname)
                try:
                    if os.path.getmtime(fpath) < threshold:
                        os.remove(fpath)
                        removed[dir_name].append(fpath)
                except OSError:
                    logger.exception("Failed to remove %s", fpath)
            # Remove empty directories
            for dname in dirs:
                dpath = os.path.join(root, dname)
                try:
                    if not os.listdir(dpath):
                        os.rmdir(dpath)
                except OSError:
                    pass

    total = sum(len(v) for v in removed.values())
    if total:
        logger.info("Cleaned up %d old files (audiobooks=%d, tmp=%d)",
                     total, len(removed["audiobooks"]), len(removed["tmp"]))
    return removed
