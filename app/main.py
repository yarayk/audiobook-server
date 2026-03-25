import logging

from fastapi import FastAPI

from app.middleware import log_requests
from app.middleware.rate_limit import rate_limit
from app.routes.download import router as download_router
from app.routes.pdf import router as pdf_router
from app.routes.tasks import router as tasks_router
from app.routes.upload import router as upload_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

app = FastAPI(title="Audiobook Server API", version="1.0.0")

app.middleware("http")(rate_limit)
app.middleware("http")(log_requests)

app.include_router(tasks_router, prefix="/api/v1")
app.include_router(upload_router, prefix="/api/v1")
app.include_router(download_router, prefix="/api/v1")
app.include_router(pdf_router, prefix="/api/v1")


@app.get("/health")
def health():
    return {"status": "ok"}
