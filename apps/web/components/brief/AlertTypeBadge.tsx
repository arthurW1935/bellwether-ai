import React from 'react';
import { AlertType } from '@/lib/types';
import { UserMinus, Zap, Map, Activity, RefreshCw, Info } from 'lucide-react';

interface AlertTypeBadgeProps {
  alert_type: AlertType;
}

export function AlertTypeBadge({ alert_type }: AlertTypeBadgeProps) {
  const config = {
    talent_poaching: { icon: UserMinus, label: "Talent Poaching" },
    competitive: { icon: Zap, label: "Competitive" },
    roadmap: { icon: Map, label: "Roadmap" },
    health: { icon: Activity, label: "Health" },
    reopen: { icon: RefreshCw, label: "Reopen" },
    routine: { icon: Info, label: "Routine" }
  };

  const { icon: Icon, label } = config[alert_type];

  return (
    <span className="flex items-center gap-1.5 bg-slate-800 text-slate-300 border border-slate-700 rounded-full px-2.5 py-0.5 text-xs font-medium">
      <Icon className="w-3 h-3" />
      {label}
    </span>
  );
}
