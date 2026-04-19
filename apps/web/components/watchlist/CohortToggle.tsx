"use client";

import React from 'react';
import { Cohort } from '@/lib/types';
import { cn } from '@/lib/cn';

interface CohortToggleProps {
  value: Cohort;
  onChange: (cohort: Cohort) => void;
  counts?: { invested: number; watching: number };
}

export function CohortToggle({ value, onChange, counts }: CohortToggleProps) {
  return (
    <div className="flex bg-slate-900 border border-slate-800 rounded-lg p-1 w-fit mb-6">
      <button
        onClick={() => onChange('invested')}
        className={cn(
          "px-4 py-1.5 text-sm rounded-md transition-colors font-medium",
          value === 'invested' ? "bg-slate-800 text-slate-100" : "text-slate-400 hover:text-slate-200"
        )}
      >
        Invested {counts ? `(${counts.invested})` : ''}
      </button>
      <button
        onClick={() => onChange('watching')}
        className={cn(
          "px-4 py-1.5 text-sm rounded-md transition-colors font-medium",
          value === 'watching' ? "bg-slate-800 text-slate-100" : "text-slate-400 hover:text-slate-200"
        )}
      >
        Watching {counts ? `(${counts.watching})` : ''}
      </button>
    </div>
  );
}
