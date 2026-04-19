"use client";

import React, { useState } from 'react';
import { Company } from '@/lib/types';
import { Button } from '@/components/common/Button';
import { Plus, Check, Loader2 } from 'lucide-react';
import { addToWatchlist } from '@/lib/api';
import { CohortBadge } from '@/components/brief/CohortBadge';

interface ResultCardProps {
  company: Company;
  onAdded: (company: Company) => void;
}

export function ResultCard({ company, onAdded }: ResultCardProps) {
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState<"idle" | "added" | "already_tracking">("idle");

  const handleAdd = async (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    
    setLoading(true);
    try {
      await addToWatchlist(company.id, "watching");
      setStatus("added");
      onAdded(company);
    } catch (err: unknown) {
      const errorMsg = (err as Error).message || "";
      if (errorMsg.toLowerCase().includes("already")) {
        setStatus("already_tracking");
      } else {
        console.error(err);
      }
    } finally {
      setLoading(false);
    }
  };

  const execsStr = company.key_execs && company.key_execs.length > 0
    ? company.key_execs.slice(0, 2).map(e => `${e.name} (${e.role})`).join(', ')
    : "—";

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 hover:border-slate-700 transition-colors cursor-pointer flex flex-col h-full relative">
      <div className="absolute top-5 right-5">
        {company.cohort && <CohortBadge cohort={company.cohort} />}
      </div>

      <div className="mb-6 pr-24">
        <a href="#" className="font-semibold text-slate-100 hover:underline">{company.name}</a>
        <div className="text-slate-500 text-sm mt-0.5">{company.domain}</div>
      </div>
      
      <div className="space-y-3 mt-auto mb-6">
        <div className="flex justify-between items-center border-b border-slate-800 pb-2">
          <span className="text-slate-500 text-xs uppercase tracking-wide">Headcount</span>
          <span className="text-slate-200 text-sm">{company.headcount ?? "—"}</span>
        </div>
        <div className="flex justify-between items-center border-b border-slate-800 pb-2">
          <span className="text-slate-500 text-xs uppercase tracking-wide">Last funding</span>
          <span className="text-slate-200 text-sm truncate max-w-[150px] text-right" title={company.last_funding ?? ""}>
            {company.last_funding ?? "—"}
          </span>
        </div>
        <div className="flex flex-col gap-1 pt-1">
          <span className="text-slate-500 text-xs uppercase tracking-wide">Key execs</span>
          <span className="text-slate-200 text-sm leading-snug line-clamp-2">{execsStr}</span>
        </div>
      </div>

      <div className="flex justify-end mt-auto">
        <Button 
          variant="primary" 
          size="sm" 
          onClick={handleAdd}
          disabled={loading || status !== "idle"}
          className={status === "added" ? "bg-emerald-600 hover:bg-emerald-600 disabled:opacity-100" : ""}
        >
          {loading ? (
            <Loader2 className="w-4 h-4 mr-2 animate-spin" />
          ) : status === "added" ? (
            <Check className="w-4 h-4 mr-2" />
          ) : status === "already_tracking" ? (
            null
          ) : (
            <Plus className="w-4 h-4 mr-2" />
          )}
          {status === "added" ? "Added" : status === "already_tracking" ? "Already tracking" : "Add to Watching"}
        </Button>
      </div>
    </div>
  );
}
