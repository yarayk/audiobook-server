import logging
import platform

from redis import Redis
from rq import Queue, SimpleWorker
from rq.timeouts import TimerDeathPenalty, UnixSignalDeathPenalty

from app import config

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)


def main():
    conn = Redis(host=config.REDIS_HOST, port=config.REDIS_PORT)
    queue = Queue("audiobook", connection=conn, default_timeout=config.JOB_TIMEOUT)

    logger.info("Starting worker on queue 'audiobook' (redis=%s:%s)", config.REDIS_HOST, config.REDIS_PORT)

    worker = SimpleWorker([queue], connection=conn)
    if platform.system() == "Windows":
        worker.death_penalty_class = TimerDeathPenalty
    worker.work()


if __name__ == "__main__":
    main()
