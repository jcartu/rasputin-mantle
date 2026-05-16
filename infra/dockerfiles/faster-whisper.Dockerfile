# infra/dockerfiles/faster-whisper.Dockerfile
# FastAPI server wrapping faster-whisper for low-latency STT.
FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg curl \
 && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
    faster-whisper>=1.0,<2 \\
    fastapi>=0.115,<1 \\
    uvicorn[standard]>=0.32,<1 \\
    python-multipart>=0.0.9,<1 \\
    httpx>=0.27,<1

WORKDIR /app

RUN cat > /app/server.py <<'EOF'
from __future__ import annotations
import os, time
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from faster_whisper import WhisperModel

app = FastAPI()

MODEL_NAME = os.environ.get("WHISPER_MODEL", "large-v3")
DEVICE     = os.environ.get("WHISPER_DEVICE", "cpu")
COMPUTE    = os.environ.get("WHISPER_COMPUTE", "int8")

print(f"loading whisper: {MODEL_NAME} on {DEVICE} ({COMPUTE})")
model = WhisperModel(MODEL_NAME, device=DEVICE, compute_type=COMPUTE, download_root="/models")
print("whisper ready")


@app.get("/health")
def health():
    return {"status": "ok", "model": MODEL_NAME, "device": DEVICE}


@app.post("/transcribe")
async def transcribe(audio: UploadFile = File(...), language: str | None = None):
    if not audio.filename:
        raise HTTPException(400, "no audio file")
    tmp = f"/tmp/{int(time.time() * 1000)}_{audio.filename}"
    with open(tmp, "wb") as f:
        f.write(await audio.read())
    t0 = time.perf_counter()
    segments, info = model.transcribe(tmp, language=language, beam_size=1, vad_filter=True)
    text = "".join(seg.text for seg in segments).strip()
    latency = (time.perf_counter() - t0) * 1000
    os.unlink(tmp)
    return JSONResponse({
        "text": text,
        "language": info.language,
        "language_probability": info.language_probability,
        "duration_ms": int(info.duration * 1000),
        "latency_ms": int(latency),
    })
EOF

EXPOSE 8803
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8803"]
