# Audiobook Server

Backend for a mobile app "Читалка с озвучкой книг" (Reading App with Book Audiobooks). Accepts ebook files, converts them to audiobooks using ebook2audiobook Docker container, and serves the results.

## Stack

- **Runtime**: Python 3.10+ with FastAPI
- **Task Queue**: RQ (Redis Queue)
- **Message Broker**: Redis
- **TTS Engine**: ebook2audiobook Docker container
- **PDF Conversion**: iLovePDF API (optional)

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy .env.example to .env:

```bash
cp .env.example .env
```

Required: ILOVEPDF_PUBLIC_KEY and ILOVEPDF_SECRET_KEY

### 3. Start Redis

```bash
docker-compose up -d
```

### 4. Start the Worker

```bash
python -m app.worker
```

### 5. Start the API Server

```bash
uvicorn app.main:app --reload
```

API at http://localhost:8000, docs at /docs

## API Endpoints

### Upload Ebook

**POST /api/v1/upload**

Upload ebook file (txt, epub, mobi, fb2, docx, pdf, html, rtf). Max 50 MB.

Response:
```json
{
  "file_id": "a1b2c3d4",
  "filename": "a1b2c3d4.epub",
  "original_name": "mybook.epub",
  "size": 1234567
}
```

### Create Task

**POST /api/v1/tasks**

```json
{
  "filename": "a1b2c3d4.epub",
  "language": "eng"
}
```

Response:
```json
{
  "task_id": "e5f6g7h8",
  "status": "pending"
}
```

Returns existing task if one already pending/processing. Fails if >= 5 concurrent tasks.

### Check Status

**GET /api/v1/tasks/{task_id}**

### Download Audiobook

**GET /api/v1/tasks/{task_id}/download**

### Convert PDF

**POST /api/v1/pdf/convert**

Convert PDF to text via iLovePDF API. Returns with converted file in ebooks/.

### Health Check

**GET /health**

## Supported Languages

English (eng/en), Russian (rus/ru), German (deu/de), French (fra/fr), Spanish (spa/es), Italian (ita/it), Portuguese (por/pt), Polish (pol/pl), Turkish (tur/tr), Dutch (nld/nl), Chinese (zho/zh), Japanese (jpn/ja), Korean (kor/ko), Hindi (hin/hi).

## Configuration

All via environment variables:

**Core**: REDIS_HOST (localhost), REDIS_PORT (6379), JOB_TIMEOUT (3600), DOCKER_IMAGE

**Paths**: EBOOKS_DIR, AUDIOBOOKS_DIR, MODELS_DIR, VOICES_DIR, TMP_DIR

**Upload**: MAX_FILE_SIZE (50 MB), PDF_CONVERT_TIMEOUT (30s)

**PDF**: ILOVEPDF_PUBLIC_KEY, ILOVEPDF_SECRET_KEY

**Rate limit**: MAX_CONCURRENT_TASKS (5), RATE_LIMIT_GENERAL (30/min), RATE_LIMIT_TASKS (5/min)

**Cleanup**: FILE_RETENTION_HOURS (24)

## Project Structure

```
app/
  config.py              - settings
  main.py                - FastAPI app
  tasks.py               - RQ jobs
  worker.py              - RQ worker + cleanup
  middleware/
    rate_limit.py        - IP-based rate limiting
  routes/
    tasks.py, upload.py, pdf.py, download.py
  models/
    task.py              - Task + Redis operations
  services/
    docker_runner.py, pdf_converter.py, cleanup.py
```

## Error Codes

- 200: OK
- 400: Bad request (format, language, file not found)
- 404: Not found (task, file)
- 413: Payload too large
- 429: Rate limit / queue full
- 502: External API error (iLovePDF)

## Task States

Pending -> Processing -> Done (or Error)

Stale detection: processing > 1 hour -> Error

## Known Issues

- ebook2audiobook --session broken
- GPU cu128 incompatible with RTX 3050 Ti
- Russian XTTSv2 needs voice .wav file
- XTTSv2 ~1.87 GB, needs 5+ GB RAM
- iLovePDF: 250/month free tier

## License

MIT
