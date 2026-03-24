import logging
import os

from app import config
from app.models.task import update_task_status
from app.services.docker_runner import ConversionPayload, run_conversion

logger = logging.getLogger(__name__)


def generate_audiobook(
    task_id: str,
    filename: str,
    language: str = "eng",
    tts_engine: str | None = None,
    voice: str | None = None,
    speed: float = 1.0,
) -> dict:
    logger.info("Task %s: starting conversion of %s (lang=%s)", task_id, filename, language)
    update_task_status(task_id, "processing")

    ebook_path = os.path.join(config.EBOOKS_DIR, filename)
    payload = ConversionPayload(
        ebook_path=ebook_path,
        language=language,
        tts_engine=tts_engine,
        voice=voice,
        speed=speed,
    )

    try:
        result = run_conversion(payload)
    except Exception as e:
        update_task_status(task_id, "error", error=str(e))
        raise

    if result.status != "done":
        update_task_status(task_id, "error", error=result.error)
        raise Exception(f"Conversion failed: {result.error}")

    update_task_status(
        task_id, "done",
        output_files=result.output_files,
        elapsed=result.elapsed,
    )

    return {
        "task_id": task_id,
        "status": result.status,
        "elapsed": result.elapsed,
        "output_files": result.output_files,
    }
