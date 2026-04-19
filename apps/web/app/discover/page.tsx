"use client";

import React, { useState } from 'react';
import { PageHeader } from '@/components/shell/PageHeader';
import { QueryForm } from '@/components/discover/QueryForm';
import { ParsedFilters } from '@/components/discover/ParsedFilters';
import { ResultList } from '@/components/discover/ResultList';
import { LoadingState } from '@/components/common/LoadingState';
import { EmptyState } from '@/components/common/EmptyState';
import { ErrorToast } from '@/components/common/ErrorToast';
import { discover } from '@/lib/api';
import { Company } from '@/lib/types';
import { Sparkles, SearchX } from 'lucide-react';

export default function DiscoverPage() {
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<{ companies: Company[]; parsed_filters: { description: string } } | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async (query: string) => {
    setLoading(true);
    setError(null);
    setResults(null);
    try {
      const data = await discover(query);
      setResults(data);
    } catch (err: unknown) {
      setError((err as Error).message || "Failed to search companies");
    } finally {
      setLoading(false);
    }
  };

  const handleCompanyAdded = () => {
    // Already handled locally by ResultCard
  };

  return (
    <div>
      <PageHeader 
        title="Discover" 
        subtitle="Describe the companies you want to find." 
      />
      
      {error && <ErrorToast message={error} onDismiss={() => setError(null)} />}
      
      <QueryForm onSubmit={handleSearch} loading={loading} />
      
      {loading ? (
        <LoadingState rows={6} />
      ) : results ? (
        results.companies.length === 0 ? (
          <EmptyState 
            icon={<SearchX />}
            title="No matches"
            description="Try broadening your query."
          />
        ) : (
          <>
            <ParsedFilters description={results.parsed_filters.description} />
            <ResultList companies={results.companies} onCompanyAdded={handleCompanyAdded} />
          </>
        )
      ) : (
        <EmptyState 
          icon={<Sparkles />}
          title="Start with a thesis"
          description="Describe what you're looking for in plain English. The agent will translate it into filters."
        />
      )}
    </div>
  );
}
