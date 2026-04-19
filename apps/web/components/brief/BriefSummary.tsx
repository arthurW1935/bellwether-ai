import React from 'react';

interface BriefSummaryProps {
  summary: string;
  generated_at: string;
  counts: { p0: number; p1: number; p2: number };
}

export function BriefSummary({ summary, generated_at, counts }: BriefSummaryProps) {
  const formattedDate = new Date(generated_at).toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' });

  return (
    <div className="bg-gradient-to-br from-violet-950/40 to-slate-900 border border-violet-900/30 rounded-xl p-6 mb-8">
      <div className="text-violet-400 text-xs uppercase tracking-wide font-medium">Today&apos;s brief</div>
      <div className="text-slate-100 text-lg leading-relaxed mt-2 mb-6 font-medium">
        {summary}
      </div>
      <div className="flex items-center gap-4 text-xs font-medium border-t border-slate-800 pt-4">
        <div className="text-slate-500">Updated {formattedDate}</div>
        <div className="flex items-center gap-2">
          <span className="bg-rose-500/10 text-rose-400 border border-rose-500/20 rounded-full px-2 py-0.5">{counts.p0} P0</span>
          <span className="bg-amber-500/10 text-amber-400 border border-amber-500/20 rounded-full px-2 py-0.5">{counts.p1} P1</span>
          <span className="bg-slate-500/10 text-slate-400 border border-slate-500/20 rounded-full px-2 py-0.5">{counts.p2} P2</span>
        </div>
      </div>
    </div>
  );
}
