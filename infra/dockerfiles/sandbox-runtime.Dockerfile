# infra/dockerfiles/sandbox-runtime.Dockerfile
# Per-task isolated sandbox the agent's CodeAct steps execute inside.
# Non-root, no-new-privileges, capability-dropped at runtime.

FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl wget jq ripgrep \
    build-essential pkg-config \
    libpq-dev \
    ffmpeg imagemagick \
    chromium chromium-driver \
    fonts-liberation \
    ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# Common data + dev packages CodeAct's tools expect.
RUN pip install --no-cache-dir \
    numpy pandas scipy scikit-learn matplotlib seaborn \
    requests httpx pydantic \
    beautifulsoup4 lxml selectolax \
    playwright \
    pytest pytest-asyncio \
    fastapi uvicorn \
    sqlalchemy psycopg[binary] \
    openpyxl python-docx pypdf \
    pillow pytesseract \
    pyyaml toml rich

# Playwright browsers
RUN python -m playwright install chromium

# Non-root user — sandbox processes run here.
RUN groupadd -g 1000 sandbox && useradd -u 1000 -g 1000 -m -s /bin/bash sandbox
USER sandbox
WORKDIR /workspace

# Tighten default umask
RUN echo 'umask 077' >> /home/sandbox/.bashrc

# Default command: nothing. The sandbox is spawned with the agent's command.
CMD ["bash"]
