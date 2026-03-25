import logging

from fastapi import Request
from fastapi.responses import JSONResponse
from redis import Redis

from app import config

logger = logging.getLogger(__name__)


def _get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


async def rate_limit(request: Request, call_next):
    client_ip = _get_client_ip(request)
    conn = Redis(host=config.REDIS_HOST, port=config.REDIS_PORT)

    is_task_create = request.method == "POST" and request.url.path.rstrip("/").endswith("/tasks")

    if is_task_create:
        key = f"ratelimit:tasks:{client_ip}"
        limit = config.RATE_LIMIT_TASKS
    else:
        key = f"ratelimit:general:{client_ip}"
        limit = config.RATE_LIMIT_GENERAL

    try:
        current = conn.incr(key)
        if current == 1:
            conn.expire(key, 60)

        if current > limit:
            logger.warning("Rate limit exceeded for %s (key=%s, count=%d)", client_ip, key, current)
            return JSONResponse(
                status_code=429,
                content={"detail": "Слишком много запросов, попробуйте позже"},
                headers={"Retry-After": "60"},
            )
    except Exception:
        logger.exception("Rate limit check failed, allowing request")

    return await call_next(request)
