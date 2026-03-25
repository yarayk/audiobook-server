import logging
import platform
import threading
import time

from redis import Redis
from rq import Queue, SimpleWorker
from rq.timeouts import TimerDeathPenalty, UnixSignalDeathPenalty

from app import config
from app.models.task import cleanup_stale_tasks
from app.services.cleanup import cleanup_old_files

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)

CLEANUP_INTERVAL = 1800  # 30 minutes


def _periodic_cleanup():
    while True:
        time.sleep(CLEANUP_INTERVAL)
        try:
            cleanup_stale_tasks()
            cleanup_old_files()
        except Exception:
            logger.exception("Periodic cleanup failed")


def main():
    conn = Redis(host=config.REDIS_HOST, port=config.REDIS_PORT)
    queue = Queue("audiobook", connection=conn, default_timeout=config.JOB_TIMEOUT)

    logger.info("Starting worker on queue 'audiobook' (redis=%s:%s)", config.REDIS_HOST, config.REDIS_PORT)

    logger.info("Running initial cleanup...")
    cleanup_stale_tasks()
    cleanup_old_files()

    cleanup_thread = threading.Thread(target=_periodic_cleanup, daemon=True)
    cleanup_thread.start()
    logger.info("Periodic cleanup thread started (every %ds)", CLEANUP_INTERVAL)

    worker = SimpleWorker([queue], connection=conn)
    if platform.system() == "Windows":
        worker.death_penalty_class = TimerDeathPenalty
    worker.work()


if __name__ == "__main__":
    main()
