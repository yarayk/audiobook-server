import os
import uuid

from fastapi import APIRouter, UploadFile

from app import config

router = APIRouter()


@router.post("/upload")
async def upload_file(file: UploadFile):
    file_id = uuid.uuid4().hex[:8]
    ext = os.path.splitext(file.filename)[1] if file.filename else ""
    saved_name = f"{file_id}{ext}"
    save_path = os.path.join(config.EBOOKS_DIR, saved_name)

    content = await file.read()
    with open(save_path, "wb") as f:
        f.write(content)

    return {
        "file_id": file_id,
        "filename": saved_name,
        "size": len(content),
    }
