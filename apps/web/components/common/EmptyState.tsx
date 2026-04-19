import React from "react";

export interface EmptyStateProps {
  icon: React.ReactNode;
  title: string;
  description: string;
  action?: React.ReactNode;
}

export function EmptyState({ icon, title, description, action }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center text-center py-16">
      <div className="text-slate-600 [&>svg]:w-12 [&>svg]:h-12">
        {icon}
      </div>
      <h3 className="text-slate-300 font-medium mt-4">{title}</h3>
      <p className="text-slate-500 text-sm mt-2 max-w-sm">{description}</p>
      {action && <div className="mt-6">{action}</div>}
    </div>
  );
}
