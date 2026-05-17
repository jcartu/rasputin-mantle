# Rasputin Mantle Desktop

Tauri 2 shell for the local Rasputin Mantle gateway. The frontend mirrors the web chat layout and uses browser `MediaRecorder` for microphone capture when the native mic plugin is not installed.

## Build

```bash
cd apps/desktop
pnpm install
pnpm build
pnpm tauri build
```

For development:

```bash
cd apps/desktop
pnpm dev
pnpm tauri dev
```

The app expects the gateway at `http://127.0.0.1:8000`. Voice transcription calls `/api/voice/transcribe`; if Faster-Whisper is not running behind the gateway, the UI reports the service as unavailable rather than fabricating a transcript.
