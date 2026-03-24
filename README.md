# Audiobook Server

Backend for a mobile reading app with audiobook generation. Accepts ebook files, converts them to audiobooks via [ebook2audiobook](https://github.com/DrewThomasson/ebook2audiobook) Docker container, and serves the result.

## Stack

- Python + FastAPI (planned)
- RQ (Redis Queue) for task management
- Redis as message broker
- ebook2audiobook Docker container for TTS

## Quick Start

### 1. Start Redis

```bash
docker-compose up -d
```

### 2. Start the worker

```bash
pip install -r requirements.txt
python -m app.worker
```

### 3. Submit a test job

```bash
python scripts/test_queue.py test.txt eng
```

## Project Structure

```
app/
  config.py              — settings (Redis, paths, timeouts)
  tasks.py               — RQ job definitions
  worker.py              — RQ worker entry point
  services/
    docker_runner.py     — ebook2audiobook Docker wrapper
scripts/
  test_queue.py          — enqueue a test conversion job
ebooks/                  — input ebook files
audiobooks/              — generated audiobooks (gitignored)
models/                  — TTS model cache
docker-compose.yml       — Redis service
```

## Supported Languages

| Language | Engine  | Notes                          |
|----------|---------|--------------------------------|
| English  | XTTSv2  | Good quality                   |
| Russian  | Fairseq | Medium quality, auto-selected  |
