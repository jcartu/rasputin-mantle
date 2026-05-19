FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir uv

COPY pyproject.toml ./
COPY packages/ /app/packages/

RUN uv pip install --system .

COPY apps/gateway /app/apps/gateway

WORKDIR /app/apps/gateway

EXPOSE 8000

CMD ["uvicorn", "gateway.app:app", "--host", "0.0.0.0", "--port", "8000"]
