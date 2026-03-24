# Audiobook Server

## Project Overview
Backend for a mobile app "Читалка с озвучкой книг". Accepts ebook files from a mobile app, generates audiobooks via ebook2audiobook Docker container, returns the result.

## Stack
- Python 3.10+ / FastAPI (planned) / RQ + Redis
- TTS: ebook2audiobook Docker container (`athomasson2/ebook2audiobook:cpu`)

## Key Commands
```bash
docker-compose up -d              # start Redis
python -m app.worker              # start RQ worker
python scripts/test_queue.py      # enqueue test job
python -m app.services.docker_runner test.txt --language eng  # direct conversion test
```

## Architecture
- `app/config.py` — env-based settings with defaults
- `app/services/docker_runner.py` — builds and runs `docker run` commands for ebook2audiobook
- `app/tasks.py` — RQ job definitions (calls docker_runner)
- `app/worker.py` — RQ worker entry point
- Queue name: `audiobook`

## ebook2audiobook Docker Details
- Headless mode: `--headless --ebook /app/ebooks/file.txt --language eng`
- Output lands in: `audiobooks/cli/cli-{session_id}/{filename}.m4b`
- Required volumes: ebooks, audiobooks, models, voices, tmp (all mapped to /app/*)
- Russian auto-selects `fairseq` engine; English uses `XTTSv2`

## Known Issues — DO NOT repeat these mistakes
- `--session` parameter is broken — never use it
- GPU tag `cu128` is incompatible with RTX 3050 Ti
- Russian on XTTSv2 requires a voice .wav file — without it, it fails
- XTTSv2 model ~1.87 GB, needs 5+ GB free RAM

## Code Conventions
- No excessive comments — clean, readable code
- Logging via standard `logging` module
- Config via environment variables with sensible defaults
- Absolute paths via `os.path` for cross-platform compatibility
