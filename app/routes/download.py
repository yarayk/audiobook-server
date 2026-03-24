import os

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.models.task import get_task

router = APIRouter()


@router.get("/tasks/{task_id}/download")
def download_result(task_id: str):
    task = get_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.status != "done":
        raise HTTPException(status_code=400, detail=f"Task is not ready (status={task.status})")

    if not task.output_files:
        raise HTTPException(status_code=400, detail="No output files")

    file_path = task.output_files[0]
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Output file not found on disk")

    return FileResponse(file_path, filename=os.path.basename(file_path))
