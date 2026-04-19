export type Cohort = "invested" | "watching";

export type AlertType =
  | "talent_poaching"
  | "competitive"
  | "roadmap"
  | "health"
  | "reopen"
  | "routine";

export type Severity = "P0" | "P1" | "P2";

export interface KeyExec {
  name: string;
  role: string;
}

export interface Company {
  id: number;
  name: string;
  domain: string;
  cohort: Cohort;
  headcount: number | null;
  last_funding: string | null;
  key_execs: KeyExec[];
  added_at: string;
}

export interface TraceStep {
  stage: string;
  summary: string;
  duration_ms: number;
  detail?: {
    api_calls?: { endpoint: string; ms: number }[];
    llm_model?: string;
    llm_tokens_in?: number;
    llm_tokens_out?: number;
  };
}

export interface Delta {
  kind: string;
  description: string;
  before: unknown;
  after: unknown;
}

export interface Alert {
  id: number;
  company: Company;
  cohort: Cohort;
  delta: Delta;
  alert_type: AlertType;
  severity: Severity;
  explanation: string;
  recommended_action: string;
  trace: TraceStep[];
  detected_at: string;
}

export interface Brief {
  summary: string;
  generated_at: string;
  alerts: Alert[];
  counts: {
    p0: number;
    p1: number;
    p2: number;
  };
}

export interface ErrorResponse {
  error: string;
  message: string;
  detail?: unknown;
}
