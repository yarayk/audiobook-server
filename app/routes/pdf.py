import os
import re
import uuid

from fastapi import APIRouter, HTTPException, UploadFile

from app import config
from app.services.pdf_converter import PDFConversionError, convert_pdf_to_text

router = APIRouter()


def _sanitize_filename(name: str) -> str:
    name = os.path.basename(name)
    name = name.replace("\x00", "")
    name = re.sub(r'[<>:"/\\|?*]', "_", name)
    return name


@router.post("/pdf/convert")
async def convert_pdf(file: UploadFile):
    original_name = _sanitize_filename(file.filename) if file.filename else ""
    ext = os.path.splitext(original_name)[1].lower()

    if ext != ".pdf":
        raise HTTPException(status_code=400, detail="Только PDF файлы поддерживаются")

    content = await file.read()

    if len(content) > config.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"Файл слишком большой ({len(content)} байт). Максимум: {config.MAX_FILE_SIZE // (1024 * 1024)} МБ",
        )

    file_id = uuid.uuid4().hex[:8]
    saved_name = f"{file_id}.pdf"
    save_path = os.path.join(config.EBOOKS_DIR, saved_name)

    with open(save_path, "wb") as f:
        f.write(content)

    try:
        output_path = convert_pdf_to_text(save_path)
    except PDFConversionError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)

    output_filename = os.path.basename(output_path)
    output_ext = os.path.splitext(output_filename)[1].lstrip(".")

    return {
        "file_id": file_id,
        "filename": output_filename,
        "original_name": original_name,
        "format": output_ext,
    }
