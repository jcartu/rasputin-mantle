# infra/dockerfiles/faster-whisper.Dockerfile


FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg curl \
 && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
    'faster-whisper>=1.0,<2' \
    'fastapi>=0.115,<1' \
    'uvicorn[standard]>=0.32,<1' \
    'python-multipart>=0.0.9,<1' \
    'httpx>=0.27,<1'

WORKDIR /app
COPY dockerfiles/faster-whisper-server.py /app/server.py

EXPOSE 8803
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8803"]
