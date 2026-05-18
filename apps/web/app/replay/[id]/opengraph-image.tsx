import { ImageResponse } from 'next/og';
import { notFound } from 'next/navigation';
import type { ReplayStep } from '@/components/session/timeline-scrubber';

export const size = { width: 1200, height: 630 };
export const contentType = 'image/png';
export const revalidate = 86400;

interface RouteProps {
  params: Promise<{ id: string }>;
}

interface ShareResponse {
  steps: ReplayStep[];
  final_answer: string | null;
}

function gatewayBase(): string {
  return process.env.MANTLE_GATEWAY_URL ?? process.env.NEXT_PUBLIC_GATEWAY_URL ?? 'http://127.0.0.1:8000';
}

function payloadData(step: ReplayStep): Record<string, unknown> {
  const data = step.payload.data;
  return typeof data === 'object' && data !== null ? data as Record<string, unknown> : {};
}

function finalScreenshot(steps: ReplayStep[]): string | null {
  for (let index = steps.length - 1; index >= 0; index -= 1) {
    const data = payloadData(steps[index]);
    for (const key of ['src', 'screenshot', 'screenshot_url', 'url']) {
      const value = data[key];
      if (typeof value === 'string' && value.length > 0) return value;
    }
  }
  return null;
}

async function fetchShare(sessionId: string): Promise<ShareResponse> {
  const response = await fetch(`${gatewayBase()}/api/share/${encodeURIComponent(sessionId)}`, {
    headers: { accept: 'application/json' },
    next: { revalidate },
  });
  if (response.status === 404) notFound();
  if (!response.ok) throw new Error(`Failed to load share (${response.status})`);
  return response.json() as Promise<ShareResponse>;
}

export default async function OpenGraphImage({ params }: RouteProps): Promise<ImageResponse> {
  const { id } = await params;
  const share = await fetchShare(id);
  const screenshot = finalScreenshot(share.steps);
  const caption = (share.final_answer ?? 'Rasputin Mantle agent replay').slice(0, 80);

  return new ImageResponse(
    (
      <div style={{ width: '100%', height: '100%', display: 'flex', position: 'relative', background: '#0b0f19', color: 'white', overflow: 'hidden' }}>
        {screenshot ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img src={screenshot} alt="Final replay screenshot" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
        ) : (
          <div style={{ width: '100%', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 54, letterSpacing: -2 }}>
            Rasputin Mantle
          </div>
        )}
        <div style={{ position: 'absolute', inset: 0, background: 'linear-gradient(180deg, rgba(0,0,0,0.08) 35%, rgba(0,0,0,0.86) 100%)' }} />
        <div style={{ position: 'absolute', left: 48, bottom: 42, right: 260, display: 'flex', flexDirection: 'column', gap: 12 }}>
          <div style={{ fontSize: 28, color: 'rgba(255,255,255,0.74)' }}>Public replay</div>
          <div style={{ fontSize: 48, fontWeight: 700, lineHeight: 1.08 }}>{caption}</div>
        </div>
        <div style={{ position: 'absolute', right: 48, bottom: 42, display: 'flex', alignItems: 'center', gap: 14, padding: '14px 18px', borderRadius: 18, background: 'rgba(11,15,25,0.72)', border: '1px solid rgba(255,255,255,0.18)' }}>
          <div style={{ width: 34, height: 34, borderRadius: 10, background: 'linear-gradient(135deg, #b897ff, #5eead4)' }} />
          <div style={{ fontSize: 30, fontWeight: 700 }}>Mantle</div>
        </div>
      </div>
    ),
    size,
  );
}
