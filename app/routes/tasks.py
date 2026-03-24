from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from redis import Redis
from rq import Queue, Retry

from app import config
from app.models.task import Task, get_task, save_task
from app.tasks import generate_audiobook

router = APIRouter()


class CreateTaskRequest(BaseModel):
    filename: str
    language: str = "eng"


class CreateTaskResponse(BaseModel):
    task_id: str
    status: str


@router.post("/tasks", response_model=CreateTaskResponse)
def create_task(req: CreateTaskRequest):
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
