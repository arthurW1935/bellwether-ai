import React from "react";

export interface LoadingStateProps {
  rows?: number;
}

export function LoadingState({ rows = 3 }: LoadingStateProps) {
  return (
    <div className="flex flex-col gap-4">
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="bg-slate-900 rounded-xl h-24 animate-pulse" />
      ))}
    </div>
  );
}
