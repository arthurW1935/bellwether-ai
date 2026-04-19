import React from 'react';
import { Company } from '@/lib/types';
import { CompanyCard } from './CompanyCard';

interface CompanyGridProps {
  companies: Company[];
}

export function CompanyGrid({ companies }: CompanyGridProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {companies.map(company => (
        <CompanyCard key={company.id} company={company} />
      ))}
    </div>
  );
}
