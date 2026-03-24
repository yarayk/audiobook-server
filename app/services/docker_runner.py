import logging
import os
import subprocess
import time
from dataclasses import dataclass, field
from typing import Optional

from app import config

logger = logging.getLogger(__name__)

RUSSIAN_LANGS = {"rus", "ru"}


@dataclass
class ConversionPayload:
    ebook_path: str
    language: str
    tts_engine: Optional[str] = None
    voice: Optional[str] = None
    speed: float = 1.0

    def __post_init__(self):
        if self.tts_engine is None:
            self.tts_engine = "fairseq" if self.language in RUSSIAN_LANGS else "XTTSv2"


@dataclass
class ConversionResult:
    status: str  # "done" | "error" | "timeout"
    elapsed: float
    output_files: list[str] = field(default_factory=list)
    exit_code: Optional[int] = None
    error: Optional[str] = None


def _host_path(local_path: str, subdir: str) -> str:
    if config.HOST_PROJECT_DIR:
        return os.path.join(config.HOST_PROJECT_DIR, subdir)
    return local_path


def build_docker_command(payload: ConversionPayload) -> list[str]:
    cmd = [
        "docker", "run", "--rm",
        "-v", f"{_host_path(config.EBOOKS_DIR, 'ebooks')}:/app/ebooks",
        "-v", f"{_host_path(config.AUDIOBOOKS_DIR, 'audiobooks')}:/app/audiobooks",
        "-v", f"{_host_path(config.MODELS_DIR, 'models')}:/app/models",
        "-v", f"{_host_path(config.VOICES_DIR, 'voices')}:/app/voices",
        "-v", f"{_host_path(config.TMP_DIR, 'tmp')}:/app/tmp",
        config.DOCKER_IMAGE,
        "--headless",
        "--ebook", f"/app/ebooks/{os.path.basename(payload.ebook_path)}",
        "--language", payload.language,
        "--tts_engine", payload.tts_engine,
        "--speed", str(payload.speed),
    ]
    if payload.voice:
        cmd += ["--voice", f"/app/voices/{os.path.basename(payload.voice)}"]
    return cmd


def _collect_files(directory: str) -> set[str]:
    result = set()
    if not os.path.exists(directory):
        return result
    for root, _, files in os.walk(directory):
        for f in files:
            result.add(os.path.join(root, f))
    return result


def run_conversion(payload: ConversionPayload) -> ConversionResult:
    if not os.path.exists(payload.ebook_path):
        logger.error("Input file not found: %s", payload.ebook_path)
        return ConversionResult(status="error", elapsed=0.0, error=f"File not found: {payload.ebook_path}")

    files_before = _collect_files(config.AUDIOBOOKS_DIR)
    cmd = build_docker_command(payload)
    logger.info("Running: %s", " ".join(cmd))

    start = time.monotonic()
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=config.JOB_TIMEOUT,
        )
        elapsed = time.monotonic() - start
    except subprocess.TimeoutExpired:
        elapsed = time.monotonic() - start
        logger.error("Docker conversion timed out after %.1fs", elapsed)
        return ConversionResult(status="timeout", elapsed=elapsed, error="Conversion timed out")

    if result.returncode != 0:
        logger.error("Docker exited with code %d\nstderr: %s", result.returncode, result.stderr)
        return ConversionResult(
            status="error",
            elapsed=elapsed,
            exit_code=result.returncode,
            error=result.stderr.strip(),
        )

    files_after = _collect_files(config.AUDIOBOOKS_DIR)
    new_files = sorted(files_after - files_before)
    logger.info("Conversion done in %.1fs, output files: %s", elapsed, new_files)

    return ConversionResult(
        status="done",
        elapsed=elapsed,
        output_files=new_files,
        exit_code=result.returncode,
    )


if __name__ == "__main__":
    import argparse

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    parser = argparse.ArgumentParser(description="Run ebook2audiobook conversion")
    parser.add_argument("ebook", help="Path to ebook file (relative to ebooks/ or absolute)")
    parser.add_argument("--language", default="eng")
    parser.add_argument("--tts_engine", default=None)
    parser.add_argument("--voice", default=None)
    parser.add_argument("--speed", type=float, default=1.0)
    args = parser.parse_args()

    ebook_path = args.ebook if os.path.isabs(args.ebook) else os.path.join(config.EBOOKS_DIR, args.ebook)
    payload = ConversionPayload(
        ebook_path=ebook_path,
        language=args.language,
        tts_engine=args.tts_engine,
        voice=args.voice,
        speed=args.speed,
    )
    res = run_conversion(payload)
    print(res)
