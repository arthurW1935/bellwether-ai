import React from 'react';
import { Severity } from '@/lib/types';
import { cn } from '@/lib/cn';

interface SeverityBadgeProps {
  severity: Severity;
}

export function SeverityBadge({ severity }: SeverityBadgeProps) {
  const styles = {
    P0: "bg-rose-500/10 text-rose-400 border-rose-500/20",
    P1: "bg-amber-500/10 text-amber-400 border-amber-500/20",
    P2: "bg-slate-500/10 text-slate-400 border-slate-500/20"
  };
  const labels = {
    P0: "Partner",
    P1: "Associate",
    P2: "Noise"
  };

  return (
    <span className={cn("rounded-full border px-2.5 py-0.5 text-xs font-medium uppercase tracking-wide", styles[severity])}>
      {labels[severity]}
    </span>
  );
}
