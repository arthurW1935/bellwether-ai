import React from 'react';
import { TraceStep } from '@/lib/types';

interface ReasoningTraceProps {
  trace: TraceStep[];
}

export function ReasoningTrace({ trace }: ReasoningTraceProps) {
  return (
    <div className="pl-2 mt-4 space-y-4 border-l border-slate-700 ml-2">
      {trace.map((step, idx) => (
        <div key={idx} className="relative pl-4">
          <div className="absolute left-[-5px] top-1.5 w-2 h-2 rounded-full bg-slate-600 border-2 border-slate-900" />
          <div className="flex justify-between items-start">
            <div>
              <div className="font-mono text-xs text-violet-400">{step.stage}</div>
              <div className="text-slate-200 text-sm mt-0.5">{step.summary}</div>
            </div>
            <div className="text-slate-500 text-xs">{step.duration_ms}ms</div>
          </div>
        </div>
      ))}
    </div>
  );
}
