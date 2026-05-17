from __future__ import annotations

import argparse
import asyncio
import json
import statistics
import time
from typing import Any

from voice.stt import STTUnavailable, transcribe
from voice.tts import TTSUnavailable, synthesize

MOCK_WAV = b"RIFF$\x00\x00\x00WAVEfmt " + (b"\x00" * 64)


async def run_latency_eval(iterations: int = 5) -> dict[str, Any]:
    latencies_ms: list[float] = []
    try:
        for _ in range(iterations):
            started = time.perf_counter()
            text = await transcribe(MOCK_WAV)
            audio = await synthesize(text or "hello", voice="default")
            if not audio:
                raise TTSUnavailable("Kokoro returned no audio")
            latencies_ms.append((time.perf_counter() - started) * 1000)
    except (STTUnavailable, TTSUnavailable) as exc:
        return {
            "skipped": True,
            "reason": str(exc),
            "iterations_requested": iterations,
            "completed": len(latencies_ms),
        }

    return {
        "skipped": False,
        "iterations": len(latencies_ms),
        "p50_ms": round(statistics.median(latencies_ms), 2),
        "p95_ms": round(_percentile(latencies_ms, 95), 2),
        "samples_ms": [round(value, 2) for value in latencies_ms],
    }


def _percentile(values: list[float], percentile: int) -> float:
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    rank = (len(ordered) - 1) * (percentile / 100)
    lower = int(rank)
    upper = min(lower + 1, len(ordered) - 1)
    weight = rank - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def main() -> None:
    parser = argparse.ArgumentParser(description="Measure Rasputin Mantle voice loop latency.")
    parser.add_argument("--iterations", type=int, default=5)
    args = parser.parse_args()
    print(json.dumps(asyncio.run(run_latency_eval(max(1, args.iterations))), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
