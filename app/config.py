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

# Host paths for Docker-in-Docker volume mounts.
# When worker runs inside a container, Docker daemon needs HOST paths, not container paths.
HOST_PROJECT_DIR = os.getenv("HOST_PROJECT_DIR", "")
