# Audiobook Server — Полный гайд по установке и запуску

## Требования

### Минимальные
- **ОС:** Windows 10/11, Linux, macOS
- **RAM:** 8 ГБ (5 ГБ свободных для TTS-модели)
- **Диск:** 15 ГБ свободного места
- **Docker Desktop:** установлен и запущен
- **Python:** 3.10+
- **Интернет:** для первого запуска (скачивание образа и модели)

### Рекомендуемые (для комфортной работы)
- **RAM:** 16 ГБ
- **GPU:** NVIDIA с CUDA 12.8+ и 4+ ГБ VRAM (ускоряет генерацию в 10-50 раз)
- **Диск:** SSD, 30+ ГБ свободного места

### Что сколько весит
| Компонент | Размер |
|-----------|--------|
| Docker-образ `ebook2audiobook:cpu` | ~5 ГБ |
| Docker-образ `ebook2audiobook:cu128` (GPU) | ~5.8 ГБ |
| TTS-модель XTTSv2 (скачивается при первом запуске) | ~1.87 ГБ |
| Docker-образ `redis:7-alpine` | ~30 МБ |
| Python-зависимости проекта | ~50 МБ |
| **Итого (CPU)** | **~7 ГБ** |
| **Итого (GPU)** | **~7.8 ГБ** |

---

## Установка с нуля

### Шаг 1: Установить Docker

**Windows:**
Скачать Docker Desktop: https://www.docker.com/products/docker-desktop
Установить, перезагрузить компьютер. Проверить:
```powershell
docker --version
```

**Linux:**
```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
# перелогиниться
docker --version
```

**macOS:**
Скачать Docker Desktop: https://www.docker.com/products/docker-desktop

### Шаг 2: Клонировать репозиторий

```bash
git clone https://github.com/<your-username>/audiobook-server.git
cd audiobook-server
```

### Шаг 3: Создать рабочие папки

**Linux/macOS:**
```bash
mkdir -p ebooks audiobooks models voices tmp
```

**Windows PowerShell:**
```powershell
"ebooks","audiobooks","models","voices","tmp" | ForEach-Object { mkdir $_ }
```

### Шаг 4: Скачать Docker-образ ebook2audiobook

**CPU (подходит всем):**
```bash
docker pull athomasson2/ebook2audiobook:cpu
```
Это займёт 5-15 минут (~5 ГБ).

**GPU (только NVIDIA + CUDA 12.8):**
```bash
docker pull athomasson2/ebook2audiobook:cu128
```

### Шаг 5: Первый запуск — скачать TTS-модель

При первом запуске контейнер скачивает модель XTTSv2 (~1.87 ГБ). Чтобы модель сохранилась в кеш и не скачивалась заново, обязательно маунтим папку `models/`:

```bash
docker run --rm -it \
  -v "./ebooks:/app/ebooks" \
  -v "./audiobooks:/app/audiobooks" \
  -v "./models:/app/models" \
  -v "./voices:/app/voices" \
  -v "./tmp:/app/tmp" \
  -p 7860:7860 \
  athomasson2/ebook2audiobook:cpu
```

**Windows PowerShell:**
```powershell
docker run --rm -it -v "${PWD}/ebooks:/app/ebooks" -v "${PWD}/audiobooks:/app/audiobooks" -v "${PWD}/models:/app/models" -v "${PWD}/voices:/app/voices" -v "${PWD}/tmp:/app/tmp" -p 7860:7860 athomasson2/ebook2audiobook:cpu
```

Дождись строки `Running on local URL: http://0.0.0.0:7860`.
Открой http://localhost:7860 — должен появиться веб-интерфейс.
Загрузи любой .txt файл, нажми конвертировать.
Когда аудио появится — контейнер работает. Останови его через `Ctrl+C`.

После этого шага в папке `models/` будут закешированные файлы модели. При следующих запусках модель загрузится из кеша за 10-15 секунд вместо повторного скачивания.

### Шаг 6: Установить Python-зависимости

```bash
pip install -r requirements.txt
```

### Шаг 7: Настроить окружение

```bash
cp .env.example .env
```

Отредактируй `.env` если нужно. Для базовой работы менять ничего не нужно — дефолты рабочие. Для PDF-конвертации добавь ключи iLovePDF.

### Шаг 8: Запуск проекта (3 терминала)

**Терминал 1 — Redis:**
```bash
docker compose up
```

**Терминал 2 — Воркер:**
```bash
python -m app.worker
```

**Терминал 3 — API-сервер:**
```bash
uvicorn app.main:app --reload
```

API доступен на http://localhost:8000
Документация (Swagger): http://localhost:8000/docs

---

## Проверка работоспособности

### Быстрый тест через curl

```bash
# 1. Healthcheck
curl http://localhost:8000/health

# 2. Создать тестовый файл
echo "Hello world. This is a test." > ebooks/test.txt

# 3. Загрузить файл
curl -X POST http://localhost:8000/api/v1/upload -F "file=@ebooks/test.txt"
# Запомни filename из ответа

# 4. Создать задачу
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Content-Type: application/json" \
  -d '{"filename": "FILENAME_ИЗ_ШАГА_3.txt", "language": "eng"}'
# Запомни task_id из ответа

# 5. Проверить статус (повторять каждые 10 сек)
curl http://localhost:8000/api/v1/tasks/TASK_ID

# 6. Скачать результат (когда status = done)
curl -O http://localhost:8000/api/v1/tasks/TASK_ID/download
```

### Тест через скрипт

```bash
python scripts/test_queue.py test.txt eng
```

---

## Настройка для Windows (8 ГБ RAM)

Если контейнер падает при загрузке модели — не хватает памяти.

**1. Создать файл WSL-конфигурации:**
```powershell
notepad "$env:USERPROFILE\.wslconfig"
```

**2. Содержимое:**
```
[wsl2]
memory=6GB
```

**3. Перезапустить WSL:**
```powershell
wsl --shutdown
```

**4. Перед запуском закрыть все лишние программы** (браузер, IDE, мессенджеры).

---

## Русский язык

### Проблема
XTTSv2 (высокое качество) не работает с русским без голосового файла.
Fairseq (среднее качество, роботизированный голос) работает из коробки.

### Текущее решение (MVP)
Для русского текста используется Fairseq:
```bash
--language rus --tts_engine fairseq
```
Сервер автоматически выбирает Fairseq для русского языка.

### Улучшение качества (после MVP)
Чтобы использовать XTTSv2 для русского, нужен голосовой файл:

**1. Требования к файлу:**
- Формат: WAV
- Длительность: 6-10 секунд
- Частота дискретизации: 24000 Hz
- Каналы: моно
- Содержание: чистый голос одного человека, без музыки и шума

**2. Как получить:**
- Записать на диктофон телефона и конвертировать в WAV 24kHz mono
- Вырезать фрагмент из подкаста или аудиокниги
- Использовать бесплатные голосовые датасеты

**3. Конвертация в нужный формат (через ffmpeg):**
```bash
ffmpeg -i input.mp3 -ar 24000 -ac 1 -acodec pcm_s16le voices/russian_male.wav
```

**4. Положить файл в папку `voices/` и использовать:**
```bash
docker run --rm -it \
  -v "./ebooks:/app/ebooks" \
  -v "./audiobooks:/app/audiobooks" \
  -v "./models:/app/models" \
  -v "./voices:/app/voices" \
  -v "./tmp:/app/tmp" \
  athomasson2/ebook2audiobook:cpu \
  --headless --ebook /app/ebooks/book.txt \
  --language rus --voice /app/voices/russian_male.wav
```

---

## GPU-ускорение

### Требования
- NVIDIA GPU с 4+ ГБ VRAM
- NVIDIA Driver 525+
- NVIDIA Container Toolkit

### Проверка
```bash
# Проверить GPU
nvidia-smi

# Проверить что Docker видит GPU
docker run --rm --gpus all nvidia/cuda:12.8.0-base-ubuntu22.04 nvidia-smi
```

### Запуск с GPU
```bash
docker pull athomasson2/ebook2audiobook:cu128

docker run --rm -it --gpus all \
  -v "./ebooks:/app/ebooks" \
  -v "./audiobooks:/app/audiobooks" \
  -v "./models:/app/models" \
  -v "./voices:/app/voices" \
  -v "./tmp:/app/tmp" \
  athomasson2/ebook2audiobook:cu128 \
  --headless --ebook /app/ebooks/book.txt --language eng
```

### Известные проблемы с GPU
- Тег `cu128` — единственный доступный GPU-тег (v26.3.10)
- Не совместим с некоторыми конфигурациями (RTX 3050 Ti, ошибка "CUDA not supported by Torch")
- Если GPU не работает — контейнер автоматически переключается на CPU

### Разница в скорости

| Размер книги | CPU | GPU |
|---|---|---|
| 4 предложения | ~5 мин | ~15 сек |
| 10 страниц | ~30-60 мин | ~3-5 мин |
| 200 страниц | ~6-12 часов | ~20-40 мин |

---

## Структура папок

```
audiobook-server/
├── app/                    # Код приложения
│   ├── main.py             # FastAPI — точка входа
│   ├── config.py           # Настройки
│   ├── tasks.py            # Задачи для RQ
│   ├── worker.py           # RQ-воркер
│   ├── middleware/
│   │   └── rate_limit.py   # Rate limiting
│   ├── routes/
│   │   ├── tasks.py        # POST/GET задач
│   │   ├── upload.py       # Загрузка файлов
│   │   ├── download.py     # Скачивание результата
│   │   └── pdf.py          # PDF-конвертация
│   ├── models/
│   │   └── task.py         # Модель задачи (Redis)
│   └── services/
│       ├── docker_runner.py    # Обёртка над ebook2audiobook
│       ├── pdf_converter.py    # iLovePDF API
│       └── cleanup.py         # Очистка старых файлов
├── scripts/
│   └── test_queue.py       # Тестовый скрипт
├── ebooks/                 # Входные файлы книг
├── audiobooks/             # Результаты генерации
│   └── cli/cli-{id}/      # Файлы по session_id
├── models/                 # Кеш TTS-моделей (~1.87 ГБ) ⚠️ НЕ УДАЛЯТЬ
├── voices/                 # Голосовые файлы для клонирования
├── tmp/                    # Временные файлы (автоочистка каждые 30 мин)
├── docker-compose.yml      # Redis
├── Dockerfile              # FastAPI образ
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

### Что в .gitignore (не коммитится)
- `audiobooks/` — результаты генерации
- `models/` — кеш моделей (1.87 ГБ)
- `voices/` — голосовые файлы
- `tmp/` — временные файлы
- `.env` — секреты

---

## Переменные окружения

| Переменная | По умолчанию | Описание |
|---|---|---|
| REDIS_HOST | localhost | Хост Redis |
| REDIS_PORT | 6379 | Порт Redis |
| JOB_TIMEOUT | 3600 | Таймаут задачи (сек) |
| DOCKER_IMAGE | athomasson2/ebook2audiobook:cpu | Docker-образ TTS |
| MAX_FILE_SIZE | 52428800 | Макс. размер файла (50 МБ) |
| MAX_CONCURRENT_TASKS | 5 | Макс. задач одновременно |
| RATE_LIMIT_GENERAL | 30 | Запросов/мин общий |
| RATE_LIMIT_TASKS | 5 | Запросов/мин на создание задач |
| FILE_RETENTION_HOURS | 24 | Хранение файлов (часов) |
| PDF_CONVERT_TIMEOUT | 30 | Таймаут PDF-конвертации (сек) |
| ILOVEPDF_PUBLIC_KEY | — | Ключ iLovePDF (для PDF) |
| ILOVEPDF_SECRET_KEY | — | Секрет iLovePDF (для PDF) |

---

## Troubleshooting

### Контейнер падает при загрузке модели
**Причина:** Не хватает RAM. Модель XTTSv2 занимает ~2 ГБ в памяти.
**Решение:** Выделить Docker минимум 6 ГБ RAM. На Windows — через `.wslconfig`.

### Модель скачивается заново при каждом запуске
**Причина:** Не маунтится папка `models/`.
**Решение:** Обязательно передавать `-v "./models:/app/models"` при docker run.

### Русский язык: "Voice not found"
**Причина:** Нет встроенного русского голоса для XTTSv2.
**Решение:** Использовать `--tts_engine fairseq` или передать свой .wav через `--voice`.

### GPU не определяется
**Причина:** Несовместимость PyTorch в контейнере с CUDA-драйвером.
**Решение:** Проверить `docker run --rm --gpus all nvidia/cuda:12.8.0-base-ubuntu22.04 nvidia-smi`. Если работает — проблема в версии PyTorch внутри контейнера. Использовать CPU.

### Ошибка "Session" при запуске
**Причина:** Баг в ebook2audiobook v25.12.20+.
**Решение:** Не использовать параметр `--session`.

### Rate limit 429
**Причина:** Превышен лимит запросов.
**Решение:** Подождать 60 секунд. Настроить лимиты через переменные окружения.

### PDF-конвертация: 502
**Причина:** iLovePDF API недоступен или закончились бесплатные запросы (250/мес).
**Решение:** Проверить ключи в `.env`. Проверить лимит на сайте iLovePDF.
