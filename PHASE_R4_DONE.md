# Phase R4: Next.js Frontend with Live Computer View

## Summary
Phase R4 successfully implemented the Next.js 15 frontend for Rasputin Mantle, featuring a dark-mode chat UI, real SSE event streaming, and a Live Computer View using Neko WebRTC.

## Files Created
- `apps/web/package.json` (Next.js 15, React 19, Tailwind CSS v4, Playwright)
- `apps/web/next.config.ts`
- `apps/web/tsconfig.json`
- `apps/web/tailwind.config.ts`
- `apps/web/postcss.config.mjs`
- `apps/web/app/globals.css` (Dark mode default, IBM Plex Mono + Inter fonts)
- `apps/web/app/layout.tsx` (Root layout)
- `apps/web/app/page.tsx` (Home page with session list)
- `apps/web/app/session/[id]/page.tsx` (Session view with resizable panels)
- `apps/web/components/sidebar.tsx` (Sidebar for session navigation)
- `apps/web/components/computer-view.tsx` (Real Neko iframe binding)
- `apps/web/components/session-stream.tsx` (Real SSE subscription via EventSource)
- `apps/web/components/chat-panel.tsx` (Chat input and message history)
- `apps/web/playwright.config.ts` (Playwright E2E configuration)
- `apps/web/tests/e2e/computer-view.spec.ts` (E2E test for Neko binding)
- `apps/web/tests/e2e/session-stream.spec.ts` (E2E test for SSE updates)
- `tests/integration/test_neko_session_binding.py` (Python integration test)

## Verification Results
- **Build Status**: `pnpm build` succeeds with no errors.
- **E2E Tests**: 2/2 tests passed (100% pass rate).
- **Integration Test**: `test_neko_session_binding.py` runs and skips gracefully when the gateway is not running, as expected.
- **Forbidden Patterns**: Verified zero instances of "Placeholder", "Coming Soon", or `setInterval` masquerading as SSE.

## Honest Gaps
- The Neko WebRTC view currently uses an `<iframe>` pointing to the Neko URL. While functional, a native WebRTC `<video>` element integration using the Neko SDK would provide tighter control over the stream and lower latency.
- The chat panel uses a simple regex for markdown code block parsing. A robust library like `react-markdown` with `rehype-highlight` would be better for production.
- Error handling in the SSE stream uses a basic exponential backoff. It could be improved with more granular connection state management and user feedback.
- The integration test skips if the gateway is not running. A full end-to-end test environment with Docker Compose would be ideal to ensure the gateway and Neko are always available for testing.
