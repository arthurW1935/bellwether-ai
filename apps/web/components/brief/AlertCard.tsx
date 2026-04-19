"use client";

import React, { useState } from 'react';
import { Alert } from '@/lib/types';
import { SeverityBadge } from './SeverityBadge';
import { CohortBadge } from './CohortBadge';
import { AlertTypeBadge } from './AlertTypeBadge';
import { ReasoningTrace } from './ReasoningTrace';
import { Button } from '@/components/common/Button';

interface AlertCardProps {
  alert: Alert;
}

export function AlertCard({ alert }: AlertCardProps) {
  const [showTrace, setShowTrace] = useState(false);

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
      <div className="flex justify-between items-start mb-3">
        <div>
          <div className="font-semibold text-slate-100">{alert.company.name}</div>
          <div className="text-slate-500 text-sm">{alert.company.domain}</div>
        </div>
        <div className="flex items-center gap-2">
          <AlertTypeBadge alert_type={alert.alert_type} />
          <CohortBadge cohort={alert.cohort} />
          <SeverityBadge severity={alert.severity} />
        </div>
      </div>
      
      <div className="text-slate-400 text-sm italic mb-4">
        &quot;{alert.delta.description}&quot;
      </div>
      
      <div className="text-slate-200 leading-relaxed mb-4 text-sm">
        {alert.explanation}
      </div>
      
      <div className="bg-emerald-950/30 border border-emerald-900/50 text-emerald-300 rounded-lg px-3 py-2 text-sm mb-4">
        <span className="font-semibold">Action:</span> {alert.recommended_action}
      </div>
      
      <div>
        <Button variant="ghost" size="sm" onClick={() => setShowTrace(!showTrace)}>
          {showTrace ? "Hide reasoning" : "Show reasoning"}
        </Button>
        {showTrace && <ReasoningTrace trace={alert.trace} />}
      </div>
    </div>
  );
}
