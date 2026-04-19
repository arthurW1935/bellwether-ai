"use client";

import React, { useEffect, useState } from 'react';
import { PageHeader } from '@/components/shell/PageHeader';
import { CohortToggle } from '@/components/watchlist/CohortToggle';
import { CompanyGrid } from '@/components/watchlist/CompanyGrid';
import { LoadingState } from '@/components/common/LoadingState';
import { EmptyState } from '@/components/common/EmptyState';
import { ErrorToast } from '@/components/common/ErrorToast';
import { Button } from '@/components/common/Button';
import { getWatchlist } from '@/lib/api';
import { Company, Cohort } from '@/lib/types';
import { Search, Building } from 'lucide-react';
import Link from 'next/link';

export default function WatchlistPage() {
  const [cohort, setCohort] = useState<Cohort>('invested');
  const [companies, setCompanies] = useState<Company[]>([]);
  const [counts, setCounts] = useState<{ invested: number; watching: number } | undefined>();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Fetch all to derive counts
    getWatchlist().then(data => {
      setCounts({
        invested: data.companies.filter(c => c.cohort === 'invested').length,
        watching: data.companies.filter(c => c.cohort === 'watching').length
      });
    }).catch(err => {
      console.error("Failed to fetch counts:", err);
    });
  }, []);

  useEffect(() => {
    setLoading(true);
    setError(null);
    getWatchlist(cohort)
      .then(data => setCompanies(data.companies))
      .catch((err: unknown) => setError((err as Error).message || "Failed to load watchlist"))
      .finally(() => setLoading(false));
  }, [cohort]);

  return (
    <div>
      <PageHeader 
        title="Watchlist" 
        subtitle="Companies you've invested in or are tracking." 
      />
      
      {error && <ErrorToast message={error} onDismiss={() => setError(null)} />}
      
      <CohortToggle value={cohort} onChange={setCohort} counts={counts} />
      
      {loading ? (
        <LoadingState rows={6} />
      ) : companies.length === 0 ? (
        cohort === 'watching' ? (
          <EmptyState 
            icon={<Search />}
            title="Nothing in your watchlist yet"
            description="Head to Discover to find companies to track."
            action={
              <Link href="/discover">
                <Button variant="primary">Discover</Button>
              </Link>
            }
          />
        ) : (
          <EmptyState 
            icon={<Building />}
            title="No portfolio loaded"
            description="Companies should be seeded on startup — check the backend."
          />
        )
      ) : (
        <CompanyGrid companies={companies} />
      )}
    </div>
  );
}
