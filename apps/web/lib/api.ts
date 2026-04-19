import { 
  Cohort, 
  Company, 
  Severity, 
  Alert, 
  Brief, 
  ErrorResponse 
} from './types';

const BASE_URL = process.env.NEXT_PUBLIC_API_URL;

async function fetchApi<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${BASE_URL || ''}${endpoint}`;
  
  const headers = new Headers(options.headers);
  if (!headers.has('Content-Type') && options.method && options.method !== 'GET') {
    headers.set('Content-Type', 'application/json');
  }

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let errorData: ErrorResponse;
    try {
      errorData = await response.json();
    } catch {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    throw new Error(errorData.message || 'An error occurred while fetching the data.');
  }

  return response.json();
}

export async function getHealth(): Promise<{ ok: boolean; version: string }> {
  return fetchApi<{ ok: boolean; version: string }>('/health');
}

export async function getWatchlist(cohort?: Cohort): Promise<{ companies: Company[] }> {
  const params = new URLSearchParams();
  if (cohort) {
    params.append('cohort', cohort);
  }
  const queryString = params.toString() ? `?${params.toString()}` : '';
  return fetchApi<{ companies: Company[] }>(`/watchlist${queryString}`);
}

export async function addToWatchlist(company_id: number, cohort: Cohort): Promise<{ company: Company }> {
  return fetchApi<{ company: Company }>('/watchlist/add', {
    method: 'POST',
    body: JSON.stringify({ company_id, cohort }),
  });
}

export async function removeFromWatchlist(company_id: number): Promise<{ removed: boolean }> {
  return fetchApi<{ removed: boolean }>('/watchlist/remove', {
    method: 'POST',
    body: JSON.stringify({ company_id }),
  });
}

export async function discover(query: string): Promise<{ companies: Company[]; parsed_filters: { description: string } }> {
  return fetchApi<{ companies: Company[]; parsed_filters: { description: string } }>('/discover', {
    method: 'POST',
    body: JSON.stringify({ query }),
  });
}

export async function getBrief(min_severity?: Severity): Promise<Brief> {
  const params = new URLSearchParams();
  if (min_severity) {
    params.append('min_severity', min_severity);
  }
  const queryString = params.toString() ? `?${params.toString()}` : '';
  return fetchApi<Brief>(`/brief${queryString}`);
}

export async function refresh(): Promise<{ brief: Brief; duration_ms: number; companies_processed: number; alerts_generated: number }> {
  return fetchApi<{ brief: Brief; duration_ms: number; companies_processed: number; alerts_generated: number }>('/refresh', {
    method: 'POST',
  });
}

export async function trigger(delta_id: string): Promise<{ alert: Alert }> {
  return fetchApi<{ alert: Alert }>('/trigger', {
    method: 'POST',
    body: JSON.stringify({ delta_id }),
  });
}

export async function getCompanyAlerts(company_id: number): Promise<{ company: Company; alerts: Alert[] }> {
  return fetchApi<{ company: Company; alerts: Alert[] }>(`/companies/${company_id}/alerts`);
}
