"use client";

import React, { useState, KeyboardEvent } from 'react';
import { Button } from '@/components/common/Button';
import { Search, Loader2 } from 'lucide-react';

interface QueryFormProps {
  onSubmit: (query: string) => void;
  loading: boolean;
}

export function QueryForm({ onSubmit, loading }: QueryFormProps) {
  const [query, setQuery] = useState("");

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
      e.preventDefault();
      if (query.trim() && !loading) {
        onSubmit(query);
      }
    }
  };

  return (
    <div className="mb-8">
      <textarea
        rows={3}
        className="bg-slate-900 border border-slate-800 rounded-xl p-4 text-slate-100 placeholder:text-slate-500 w-full resize-none focus:border-violet-500 focus:outline-none focus:ring-2 focus:ring-violet-500/20"
        placeholder="Series B fintech in India with 20% YoY headcount growth and no US VC funding yet"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onKeyDown={handleKeyDown}
      />
      <div className="mt-3 flex justify-end">
        <Button 
          variant="primary" 
          onClick={() => onSubmit(query)} 
          disabled={!query.trim() || loading}
        >
          {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Search className="w-4 h-4 mr-2" />}
          Search
        </Button>
      </div>
    </div>
  );
}
