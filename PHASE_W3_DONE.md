# Phase W3 Done — Replay Scrubber, Public Share Links, OG Images

## Completion checklist

- [x] Timeline scrubber component created with drag, keyboard, play/pause, and loading skeleton.
- [x] Finished session traces can scrub chat, screenshot, and files from persisted steps.
- [x] Public `/replay/[id]` page renders without app auth and 404s through the gateway when private.
- [x] `/api/share/{session_id}` GET/PATCH routes added with recursive secret stripping.
- [x] Share modal added with public/private toggle, copy URL, and expiry presets.
- [x] Share badge added for owner app sessions with public link and unshare action.
- [x] Next.js Open Graph image route added for shared replays.
- [x] Standalone Pillow OG image generator added at `scripts/generate-og-image.py`.
- [x] `share_public` migration added for sessions.
- [x] No API keys, sandbox credentials, auth tokens, cookies, passwords, or secrets are emitted in share responses.
