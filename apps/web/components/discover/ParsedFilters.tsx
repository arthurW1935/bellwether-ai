import React from 'react';

interface ParsedFiltersProps {
  description: string;
}

export function ParsedFilters({ description }: ParsedFiltersProps) {
  return (
    <div className="bg-slate-900/50 border border-slate-800 rounded-lg px-4 py-3 mb-6">
      <div className="text-violet-400 text-xs uppercase tracking-wide font-medium">Interpreted as</div>
      <div className="text-slate-300 text-sm mt-1">{description}</div>
    </div>
  );
}
