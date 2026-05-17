# infra/dockerfiles/kokoro.Dockerfile
FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg curl espeak-ng git \
 && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
    'fastapi>=0.115,<1' \
    'uvicorn[standard]>=0.32,<1' \
    'soundfile>=0.12,<1' \
    'numpy>=1.26,<2'

RUN pip install --no-cache-dir \
    'torch>=2.4,<3' --index-url https://download.pytorch.org/whl/cpu

RUN pip install --no-cache-dir 'kokoro>=0.3.5'

WORKDIR /app
COPY dockerfiles/kokoro-server.py /app/server.py

EXPOSE 8804
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8804"]
