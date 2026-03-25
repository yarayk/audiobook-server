import os

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from redis import Redis
from rq import Queue, Retry

from app import config
from app.models.task import Task, get_task, save_task, count_active_tasks, TASK_PREFIX, _redis
from app.tasks import generate_audiobook

router = APIRouter()


class CreateTaskRequest(BaseModel):
    filename: str
    language: str = "eng"


class CreateTaskResponse(BaseModel):
    task_id: str
    status: str


def _find_active_task(filename: str, language: str) -> Task | None:
    conn = _redis()
    for key in conn.scan_iter(f"{TASK_PREFIX}*"):
        data = conn.get(key)
        if data is None:
            continue
        task = Task.from_json(data)
        if task.filename == filename and task.language == language and task.status in ("pending", "processing"):
            return task
    return None


@router.post("/tasks", response_model=CreateTaskResponse)
def create_task(req: CreateTaskRequest):
    file_path = os.path.join(config.EBOOKS_DIR, os.path.basename(req.filename))
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail=f"File '{req.filename}' not found in ebooks/")

    if req.language not in config.SUPPORTED_LANGUAGES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported language '{req.language}'. Supported: {', '.join(sorted(config.SUPPORTED_LANGUAGES))}",
        )

    if count_active_tasks() >= config.MAX_CONCURRENT_TASKS:
        raise HTTPException(
            status_code=429,
            detail="Слишком много задач, попробуйте позже",
        )

    existing = _find_active_task(req.filename, req.language)
    if existing:
        return CreateTaskResponse(task_id=existing.task_id, status=existing.status)

    task = Task.new(filename=req.filename, language=req.language)
    save_task(task)

    conn = Redis(host=config.REDIS_HOST, port=config.REDIS_PORT)
    queue = Queue("audiobook", connection=conn, default_timeout=config.JOB_TIMEOUT)
    queue.enqueue(
        generate_audiobook,
        task_id=task.task_id,
        filename=req.filename,
        language=req.language,
        retry=Retry(max=2, interval=[30, 60]),
        job_timeout=config.JOB_TIMEOUT,
    )

    return CreateTaskResponse(task_id=task.task_id, status=task.status)


@router.get("/tasks/{task_id}")
def get_task_status(task_id: str):
    task = get_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task
