import React, { useEffect, useRef } from 'react';
import { Alert } from '@/lib/types';
import { AlertCard } from './AlertCard';

interface AlertListProps {
  alerts: Alert[];
  newAlertId?: number;
}

export function AlertList({ alerts, newAlertId }: AlertListProps) {
  const p0Alerts = alerts.filter(a => a.severity === 'P0');
  const p1Alerts = alerts.filter(a => a.severity === 'P1');

  const newAlertRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (newAlertId && newAlertRef.current) {
      newAlertRef.current.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  }, [newAlertId]);

  return (
    <div className="space-y-8">
      {p0Alerts.length > 0 && (
        <div>
          <div className="flex items-center gap-2 text-slate-500 text-xs uppercase tracking-wide mb-3 font-medium">
            <span>Partner alerts</span>
            <span className="bg-slate-800 text-slate-300 px-1.5 py-0.5 rounded-full">{p0Alerts.length}</span>
          </div>
          <div className="flex flex-col gap-4">
            {p0Alerts.map(alert => (
              <div key={alert.id} ref={alert.id === newAlertId ? newAlertRef : null}>
                <AlertCard alert={alert} />
              </div>
            ))}
          </div>
        </div>
      )}

      {p1Alerts.length > 0 && (
        <div>
          <div className="flex items-center gap-2 text-slate-500 text-xs uppercase tracking-wide mb-3 font-medium">
            <span>Associate alerts</span>
            <span className="bg-slate-800 text-slate-300 px-1.5 py-0.5 rounded-full">{p1Alerts.length}</span>
          </div>
          <div className="flex flex-col gap-4">
            {p1Alerts.map(alert => (
              <div key={alert.id} ref={alert.id === newAlertId ? newAlertRef : null}>
                <AlertCard alert={alert} />
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
