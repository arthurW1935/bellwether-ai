import React from 'react';
import { Cohort } from '@/lib/types';
import { cn } from '@/lib/cn';

interface CohortBadgeProps {
  cohort: Cohort;
}

export function CohortBadge({ cohort }: CohortBadgeProps) {
  const styles = {
    invested: "bg-violet-500/10 text-violet-400 border-violet-500/20",
    watching: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
  };
  const labels = {
    invested: "Invested",
    watching: "Watching"
  };

  return (
    <span className={cn("rounded-full border px-2.5 py-0.5 text-xs font-medium uppercase tracking-wide", styles[cohort])}>
      {labels[cohort]}
    </span>
  );
}
