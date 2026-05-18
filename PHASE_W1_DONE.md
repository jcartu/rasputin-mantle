# Phase W1 Completion Checklist

## Tauri desktop

- [x] Added `apps/desktop/tauri.conf.json` for Tauri 2 with product name, identifier, updater artifacts, updater endpoint, global Tauri, and bundle targets.
- [x] Wired Rust entrypoints with opener, updater, native menu installation, single-instance handling, and Tauri commands.
- [x] Added native File/Edit/View/Window/Help menu bar.
- [x] Added single-instance focus and `tauri://navigate` event emission for second launches.
- [x] Ensured `tauri-build` is present and package scripts reference `tauri.conf.json`.
- [x] Generated placeholder icon assets from `assets/brand/logo.jpg` at 32, 48, 64, 128, 256, and 512 px.

## Browser extension

- [x] Created `packages/browser-extension` Manifest V3 extension.
- [x] Added context menu, omnibox, side panel, active tab, and storage permissions.
- [x] Limited host permissions to the configured default gateway (`http://localhost:8000/`); no wildcard host permissions.
- [x] Implemented service worker session creation and icon state polling.
- [x] Implemented options page for gateway URL and optional bearer token.
- [x] Implemented side panel live event stream rendering.
- [x] Added build script producing `dist/extension-chrome.zip` and `dist/extension-edge.zip`.

## Guardrails

- [x] No Chromium sandbox-disabling flag added.
- [x] No Manifest V2.
- [x] No wildcard host permissions.
- [x] No mock transports.
