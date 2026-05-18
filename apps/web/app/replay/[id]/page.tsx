import type { Metadata } from 'next';
import type React from 'react';
import { notFound } from 'next/navigation';
import { ReplaySessionView } from '@/components/session/replay-session-view';
import type { ReplayStep } from '@/components/session/timeline-scrubber';

interface PageParams {
  id: string;
}

interface ReplayPageProps {
  params: Promise<PageParams>;
  searchParams: Promise<{ t?: string }>;
}

interface ShareResponse {
  session: {
    session_id: string;
    share_public: boolean;
    expires_at: string | null;
  };
  steps: ReplayStep[];
  final_answer: string | null;
}

function gatewayBase(): string {
  return process.env.MANTLE_GATEWAY_URL ?? process.env.NEXT_PUBLIC_GATEWAY_URL ?? 'http://127.0.0.1:8000';
}

async function fetchShare(sessionId: string): Promise<ShareResponse> {
  const response = await fetch(`${gatewayBase()}/api/share/${encodeURIComponent(sessionId)}`, {
    headers: { accept: 'application/json' },
    next: { revalidate: 30 },
  });
  if (response.status === 404) notFound();
  if (!response.ok) throw new Error(`Failed to load shared replay (${response.status})`);
  return response.json() as Promise<ShareResponse>;
}

export async function generateMetadata({ params }: ReplayPageProps): Promise<Metadata> {
  const { id } = await params;
  const share = await fetchShare(id);
  const title = `Mantle replay ${id}`;
  const description = share.final_answer ?? 'Watch a Rasputin Mantle agent replay.';
  return {
    title,
    description,
    openGraph: {
      title,
      description,
      type: 'article',
      images: [{ url: `/replay/${encodeURIComponent(id)}/opengraph-image`, width: 1200, height: 630 }],
    },
    twitter: {
      card: 'summary_large_image',
      title,
      description,
      images: [`/replay/${encodeURIComponent(id)}/opengraph-image`],
    },
  };
}

export default async function PublicReplayPage({ params, searchParams }: ReplayPageProps): Promise<React.ReactElement> {
  const [{ id }, query] = await Promise.all([params, searchParams]);
  const share = await fetchShare(id);
  const parsedStep = Number.parseInt(query.t ?? '', 10);
  const initialStep = Number.isFinite(parsedStep) ? parsedStep : Math.max(share.steps.length - 1, 0);

  return (
    <main style={{ height: '100vh', width: '100vw', overflow: 'hidden' }}>
      <ReplaySessionView
        sessionId={share.session.session_id}
        steps={share.steps}
        initialStep={initialStep}
        banner={(
          <div style={{ padding: 'var(--spacing-2) var(--spacing-3)', borderBottom: '1px solid var(--color-border)', color: 'var(--color-foreground-muted)', fontSize: 'var(--text-sm)' }}>
            Public Mantle replay · read-only
          </div>
        )}
      />
    </main>
  );
}
