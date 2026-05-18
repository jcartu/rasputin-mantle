'use client';

import * as React from 'react';
import { Mail, Plug, Slack } from 'lucide-react';

import { IntegrationCard } from '@/components/settings/integration-card';
import { Card, CardBody, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { useToast } from '@/components/ui/toast';
import {
  disconnectSlackIntegration,
  getMailIntegrationStatus,
  getSlackIntegrationStatus,
  type MailIntegrationStatus,
  type SlackIntegrationStatus,
} from '@/lib/api';

export default function IntegrationsPage() {
  const [slackStatus, setSlackStatus] = React.useState<SlackIntegrationStatus | null>(null);
  const [mailStatus, setMailStatus] = React.useState<MailIntegrationStatus | null>(null);
  const [loading, setLoading] = React.useState(true);
  const { toast } = useToast();

  const refresh = React.useCallback(async () => {
    const [nextSlack, nextMail] = await Promise.all([getSlackIntegrationStatus(), getMailIntegrationStatus()]);
    setSlackStatus(nextSlack);
    setMailStatus(nextMail);
  }, []);

  React.useEffect(() => {
    refresh()
      .catch((error) => toast({ title: 'Failed to load integrations', description: error instanceof Error ? error.message : 'Unknown error', variant: 'destructive' }))
      .finally(() => setLoading(false));
  }, [refresh, toast]);

  async function disconnectSlack() {
    try {
      await disconnectSlackIntegration();
      await refresh();
      toast({ title: 'Slack disconnected', variant: 'success' });
    } catch (error) {
      toast({ title: 'Failed to disconnect Slack', description: error instanceof Error ? error.message : 'Unknown error', variant: 'destructive' });
    }
  }

  return (
    <div className="container space-y-8 py-8">
      <div className="space-y-2">
        <h1 className="text-3xl font-bold tracking-tight">Integrations</h1>
        <p style={{ color: 'var(--color-foreground-muted)' }}>Connect Slack and mail channels for agent handoffs.</p>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          <Skeleton height={220} />
          <Skeleton height={220} />
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          <IntegrationCard
            name="Slack"
            description="OAuth install, slash commands, @mentions, and signed event webhooks."
            connected={Boolean(slackStatus?.connected)}
            configured={Boolean(slackStatus?.configured)}
            metadata={slackStatus?.team_name ? `Workspace: ${slackStatus.team_name}` : 'Install from /api/slack/install.'}
            actionLabel={slackStatus?.connected ? 'Disconnect' : undefined}
            onAction={slackStatus?.connected ? () => { void disconnectSlack(); } : undefined}
          />
          <IntegrationCard
            name="Mail"
            description="IMAP inbound tasks and SMTP thread replies with session links."
            connected={Boolean(mailStatus?.inbound_configured || mailStatus?.outbound_configured)}
            configured={Boolean(mailStatus?.inbound_configured || mailStatus?.outbound_configured)}
            metadata={mailStatus?.allowed_senders.length ? `Allowed: ${mailStatus.allowed_senders.join(', ')}` : 'Configure MAIL_ALLOWED_SENDERS and SMTP/IMAP env vars.'}
          />
        </div>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Configuration</CardTitle>
        </CardHeader>
        <CardBody style={{ display: 'grid', gap: 'var(--spacing-3)', color: 'var(--color-foreground-muted)' }}>
          <div className="flex items-center gap-2"><Slack size={16} /> Slack uses SLACK_CLIENT_ID, SLACK_CLIENT_SECRET, and SLACK_SIGNING_SECRET.</div>
          <div className="flex items-center gap-2"><Mail size={16} /> Mail uses MAIL_ALLOWED_SENDERS plus MAIL_IMAP_* and MAIL_SMTP_* settings.</div>
          <div className="flex items-center gap-2"><Plug size={16} /> Secrets are read from environment variables only.</div>
        </CardBody>
      </Card>
    </div>
  );
}
