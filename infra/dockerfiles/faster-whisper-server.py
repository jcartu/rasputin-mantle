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
async def transcribe(file: UploadFile = File("file"), language: str | None = None):
    if not file.filename:
        raise HTTPException(400, "no audio file")
    tmp = f"/tmp/{int(time.time() * 1000)}_{file.filename}"
    with open(tmp, "wb") as f:
        f.write(await file.read())
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
