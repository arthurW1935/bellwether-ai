import React from 'react';
import { Company } from '@/lib/types';
import { ResultCard } from './ResultCard';

interface ResultListProps {
  companies: Company[];
  onCompanyAdded: (company: Company) => void;
}

export function ResultList({ companies, onCompanyAdded }: ResultListProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {companies.map(company => (
        <ResultCard key={company.id} company={company} onAdded={onCompanyAdded} />
      ))}
    </div>
  );
}
