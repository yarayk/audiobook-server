import logging
import os

import httpx

from app import config

logger = logging.getLogger(__name__)

ILOVEPDF_API = "https://api.ilovepdf.com/v1"


class PDFConversionError(Exception):
    def __init__(self, message: str, status_code: int = 502):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


def _authenticate(client: httpx.Client) -> str:
    resp = client.post(
        f"{ILOVEPDF_API}/auth",
        json={"public_key": config.ILOVEPDF_PUBLIC_KEY},
    )
    if resp.status_code == 401:
        raise PDFConversionError("Невалидные ключи iLovePDF API", 502)
    resp.raise_for_status()
    return resp.json()["token"]


def _start_task(client: httpx.Client, token: str) -> tuple[str, str]:
    resp = client.get(
        f"{ILOVEPDF_API}/start/pdftxt",
        headers={"Authorization": f"Bearer {token}"},
    )
    resp.raise_for_status()
    data = resp.json()
    return data["server"], data["task"]


def _upload_file(client: httpx.Client, server: str, token: str, task_id: str, file_path: str) -> str:
    with open(file_path, "rb") as f:
        resp = client.post(
            f"https://{server}/v1/upload",
            headers={"Authorization": f"Bearer {token}"},
            data={"task": task_id},
            files={"file": (os.path.basename(file_path), f, "application/pdf")},
        )
    if resp.status_code == 422:
        raise PDFConversionError("Файл повреждён или не является валидным PDF", 502)
    resp.raise_for_status()
    return resp.json()["server_filename"]


def _process(client: httpx.Client, server: str, token: str, task_id: str, server_filename: str) -> None:
    resp = client.post(
        f"https://{server}/v1/process",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "task": task_id,
            "tool": "pdftxt",
            "files": [{"server_filename": server_filename, "filename": server_filename}],
        },
    )
    if resp.status_code == 429:
        raise PDFConversionError("Лимит iLovePDF API исчерпан (250 запросов/месяц)", 502)
    resp.raise_for_status()


def _download(client: httpx.Client, server: str, token: str, task_id: str, output_path: str) -> None:
    resp = client.get(
        f"https://{server}/v1/download/{task_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    resp.raise_for_status()
    with open(output_path, "wb") as f:
        f.write(resp.content)


def convert_pdf_to_text(input_path: str) -> str:
    if not config.ILOVEPDF_PUBLIC_KEY:
        raise PDFConversionError("ILOVEPDF_PUBLIC_KEY не настроен", 502)

    timeout = httpx.Timeout(config.PDF_CONVERT_TIMEOUT, connect=10.0)

    try:
        with httpx.Client(timeout=timeout) as client:
            logger.info("Authenticating with iLovePDF API")
            token = _authenticate(client)

            logger.info("Starting pdftxt task")
            server, task_id = _start_task(client, token)

            logger.info("Uploading file to iLovePDF")
            server_filename = _upload_file(client, server, token, task_id, input_path)

            logger.info("Processing PDF conversion")
            _process(client, server, token, task_id, server_filename)

            base_name = os.path.splitext(os.path.basename(input_path))[0]
            output_path = os.path.join(config.EBOOKS_DIR, f"{base_name}.txt")

            logger.info("Downloading converted file")
            _download(client, server, token, task_id, output_path)

    except PDFConversionError:
        raise
    except httpx.TimeoutException:
        raise PDFConversionError("Таймаут соединения с iLovePDF API", 502)
    except httpx.HTTPStatusError as e:
        raise PDFConversionError(f"Ошибка iLovePDF API: {e.response.status_code}", 502)
    except httpx.ConnectError:
        raise PDFConversionError("Не удалось подключиться к iLovePDF API", 502)

    logger.info("PDF converted successfully: %s → %s", input_path, output_path)
    return output_path
