import logging
import time
import traceback

from fastapi import Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


async def log_requests(request: Request, call_next):
    start = time.monotonic()
    try:
        response = await call_next(request)
    except Exception:
        elapsed = time.monotonic() - start
        logger.error(
            "%s %s 500 %.3fs\n%s",
            request.method, request.url.path, elapsed, traceback.format_exc(),
        )
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error"},
        )

    elapsed = time.monotonic() - start
    logger.info("%s %s %d %.3fs", request.method, request.url.path, response.status_code, elapsed)
    return response
