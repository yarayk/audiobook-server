import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

EBOOKS_DIR = os.getenv("EBOOKS_DIR", os.path.join(BASE_DIR, "ebooks"))
AUDIOBOOKS_DIR = os.getenv("AUDIOBOOKS_DIR", os.path.join(BASE_DIR, "audiobooks"))
MODELS_DIR = os.getenv("MODELS_DIR", os.path.join(BASE_DIR, "models"))
VOICES_DIR = os.getenv("VOICES_DIR", os.path.join(BASE_DIR, "voices"))
TMP_DIR = os.getenv("TMP_DIR", os.path.join(BASE_DIR, "tmp"))

DOCKER_IMAGE = os.getenv("DOCKER_IMAGE", "athomasson2/ebook2audiobook:cpu")
JOB_TIMEOUT = int(os.getenv("JOB_TIMEOUT", "3600"))

MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", str(50 * 1024 * 1024)))  # 50 MB
ALLOWED_EXTENSIONS = {".txt", ".epub", ".mobi", ".fb2", ".docx", ".pdf", ".html", ".rtf"}
SUPPORTED_LANGUAGES = {
    "eng", "rus", "deu", "fra", "spa", "ita", "por", "pol", "tur", "nld", "zho", "jpn", "kor", "hin",
    "en", "ru", "de", "fr", "es", "it", "pt", "pl", "tr", "nl", "zh", "ja", "ko", "hi",
}

MAX_CONCURRENT_TASKS = int(os.getenv("MAX_CONCURRENT_TASKS", "5"))
RATE_LIMIT_GENERAL = int(os.getenv("RATE_LIMIT_GENERAL", "30"))
RATE_LIMIT_TASKS = int(os.getenv("RATE_LIMIT_TASKS", "5"))
FILE_RETENTION_HOURS = int(os.getenv("FILE_RETENTION_HOURS", "24"))

# Host paths for Docker-in-Docker volume mounts.
# When worker runs inside a container, Docker daemon needs HOST paths, not container paths.
HOST_PROJECT_DIR = os.getenv("HOST_PROJECT_DIR", "")
