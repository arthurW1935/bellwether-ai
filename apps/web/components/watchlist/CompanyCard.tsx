import React from 'react';
import { Company } from '@/lib/types';
import { CohortBadge } from '@/components/brief/CohortBadge';

interface CompanyCardProps {
  company: Company;
}

export function CompanyCard({ company }: CompanyCardProps) {
  const execsStr = company.key_execs && company.key_execs.length > 0
    ? company.key_execs.slice(0, 2).map(e => `${e.name} (${e.role})`).join(', ')
    : "—";

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 hover:border-slate-700 transition-colors cursor-pointer relative flex flex-col h-full">
      <div className="absolute top-5 right-5">
        <CohortBadge cohort={company.cohort} />
      </div>
      
      <div className="mb-6 pr-24">
        <a href="#" className="font-semibold text-slate-100 hover:underline">{company.name}</a>
        <div className="text-slate-500 text-sm mt-0.5">{company.domain}</div>
      </div>
      
      <div className="space-y-3 mt-auto">
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
    </div>
  );
}
