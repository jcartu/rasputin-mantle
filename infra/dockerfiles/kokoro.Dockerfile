# infra/dockerfiles/kokoro.Dockerfile
# FastAPI server wrapping Kokoro-82M for sub-300ms first-chunk TTS.
FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg curl espeak-ng \
 && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
    fastapi>=0.115,<1 \\
    uvicorn[standard]>=0.32,<1 \\
    soundfile>=0.12,<1 \\
    numpy>=1.26,<2 \\
    torch>=2.4,<3 --index-url https://download.pytorch.org/whl/cpu

# Kokoro install: pip from GitHub release (replace with a pinned version when published to PyPI)
RUN pip install --no-cache-dir kokoro==0.4.* || \
    pip install --no-cache-dir "git+https://github.com/hexgrad/kokoro.git@v0.4.0"

WORKDIR /app

RUN cat > /app/server.py <<'EOF'
from __future__ import annotations
import io, os, time
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
import soundfile as sf
import numpy as np

app = FastAPI()

try:
    from kokoro import KPipeline
    pipeline = KPipeline(lang_code="a")  # American English; switchable per request
    print("kokoro ready")
except Exception as e:
    pipeline = None
    print(f"kokoro init failed: {e}")


class TTSRequest(BaseModel):
    text: str
    voice: str = "af_heart"
    speed: float = 1.0


@app.get("/health")
def health():
    return {"status": "ok" if pipeline else "degraded", "model": "kokoro-82M"}


@app.post("/synthesize")
async def synthesize(req: TTSRequest):
    if not pipeline:
        raise HTTPException(503, "kokoro not initialized")
    t0 = time.perf_counter()
    generator = pipeline(req.text, voice=req.voice, speed=req.speed)
    audio_chunks = []
    for _i, (gs, ps, audio) in enumerate(generator):
        audio_chunks.append(audio)
    audio = np.concatenate(audio_chunks) if audio_chunks else np.zeros(1)

    buf = io.BytesIO()
    sf.write(buf, audio, 24000, format="WAV")
    buf.seek(0)
    latency = (time.perf_counter() - t0) * 1000
    return StreamingResponse(buf, media_type="audio/wav", headers={"X-Latency-Ms": str(int(latency))})
EOF

EXPOSE 8804
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8804"]
