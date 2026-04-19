"use client";

import React, { useEffect, useState } from 'react';
import { PageHeader } from '@/components/shell/PageHeader';
import { Button } from '@/components/common/Button';
import { LoadingState } from '@/components/common/LoadingState';
import { EmptyState } from '@/components/common/EmptyState';
import { ErrorToast } from '@/components/common/ErrorToast';
import { BriefSummary } from '@/components/brief/BriefSummary';
import { AlertList } from '@/components/brief/AlertList';
import { TriggerButton } from '@/components/brief/TriggerButton';
import { getBrief, refresh } from '@/lib/api';
import { Brief, Alert } from '@/lib/types';
import { Inbox, Loader2, RefreshCw } from 'lucide-react';

export default function BriefPage() {
  const [brief, setBrief] = useState<Brief | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [newAlertId, setNewAlertId] = useState<number | undefined>();

  const loadBrief = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getBrief();
      setBrief(data);
    } catch (err: unknown) {
      setError((err as Error).message || "Failed to load brief");
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    setError(null);
    try {
      const data = await refresh();
      setBrief(data.brief);
    } catch (err: unknown) {
      setError((err as Error).message || "Failed to refresh brief");
    } finally {
      setRefreshing(false);
    }
  };

  useEffect(() => {
    loadBrief();
  }, []);

  const handleTriggered = (alert: Alert) => {
    if (brief) {
      setBrief({
        ...brief,
        alerts: [alert, ...brief.alerts],
        counts: {
          ...brief.counts,
          [alert.severity.toLowerCase() as keyof typeof brief.counts]: brief.counts[alert.severity.toLowerCase() as keyof typeof brief.counts] + 1
        }
      });
      setNewAlertId(alert.id);
    } else {
      // If there's no brief yet, we probably want to just reload it
      loadBrief();
    }
  };

  const actions = (
    <>
      <TriggerButton onTriggered={handleTriggered} onError={setError} />
      <Button variant="primary" onClick={handleRefresh} disabled={refreshing || loading}>
        {refreshing ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <RefreshCw className="w-4 h-4 mr-2" />}
        Refresh
      </Button>
    </>
  );

  return (
    <div>
      <PageHeader title="Today's Brief" actions={actions} />
      
      {error && <ErrorToast message={error} onDismiss={() => setError(null)} />}

      {loading ? (
        <LoadingState rows={5} />
      ) : !brief || brief.alerts.length === 0 ? (
        <EmptyState 
          icon={<Inbox />} 
          title="No alerts yet" 
          description="Refresh to generate today's brief." 
          action={
            <Button variant="primary" onClick={handleRefresh} disabled={refreshing}>
              {refreshing ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <RefreshCw className="w-4 h-4 mr-2" />}
              Refresh
            </Button>
          } 
        />
      ) : (
        <>
          <BriefSummary summary={brief.summary} generated_at={brief.generated_at} counts={brief.counts} />
          <AlertList alerts={brief.alerts} newAlertId={newAlertId} />
        </>
      )}
    </div>
  );
}
