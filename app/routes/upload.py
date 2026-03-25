import os
import re
import uuid

from fastapi import APIRouter, HTTPException, UploadFile

from app import config

router = APIRouter()


def _sanitize_filename(name: str) -> str:
    name = os.path.basename(name)
    name = name.replace("\x00", "")
    name = re.sub(r'[<>:"/\\|?*]', "_", name)
    return name


@router.post("/upload")
async def upload_file(file: UploadFile):
    original_name = _sanitize_filename(file.filename) if file.filename else ""
    ext = os.path.splitext(original_name)[1].lower()

    if ext not in config.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported format '{ext}'. Allowed: {', '.join(sorted(config.ALLOWED_EXTENSIONS))}",
        )

    content = await file.read()

    if len(content) > config.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File too large ({len(content)} bytes). Maximum: {config.MAX_FILE_SIZE} bytes ({config.MAX_FILE_SIZE // (1024 * 1024)} MB)",
        )

    file_id = uuid.uuid4().hex[:8]
    saved_name = f"{file_id}{ext}"
    save_path = os.path.join(config.EBOOKS_DIR, saved_name)

    with open(save_path, "wb") as f:
        f.write(content)

    return {
        "file_id": file_id,
        "filename": saved_name,
        "original_name": original_name,
        "size": len(content),
    }
