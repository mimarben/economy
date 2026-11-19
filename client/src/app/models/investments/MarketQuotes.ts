/* eslint-disable */
/**
 * Models for market quotes and the investments dashboard.
 * Hand-written (not schema-generated): these endpoints return computed
 * payloads (joins of contributions + cached quotes), not CRUD entities.
 */

/** Quote status: ok = fresh, stale = cached older than TTL, unavailable = no data. */
export type QuoteStatus = 'ok' | 'stale' | 'unavailable';

export interface MarketQuote {
  isin: string;
  symbol?: string | null;
  name?: string | null;
  instrument_type?: string | null;
  currency?: string | null;
  last_price?: number | null;
  previous_close?: number | null;
  change_abs?: number | null;
  change_pct?: number | null;
  source?: string | null;
  fetched_at?: string | null;
  status: QuoteStatus;
}

export interface DashboardEntry extends Omit<MarketQuote, 'status'> {
  isin: string;
  total_contributed: number;
  contributions: number;
  last_contribution_date?: string | null;
  /** Units held from the latest investment log; null = never logged. */
  units?: number | null;
  /** True when some contributions of this ISIN have no log. */
  units_partial: boolean;
  /** Last hand-recorded valuation (sum of latest log current_value). */
  reported_value?: number | null;
  /** units x last_price, when both are known. */
  market_value?: number | null;
  /** market_value - total_contributed. */
  unrealized_pl?: number | null;
  unrealized_pl_pct?: number | null;
  quote_status: QuoteStatus;
}

export interface InvestmentsDashboard {
  entries: DashboardEntry[];
  without_isin_count: number;
  without_isin_amount: number;
  total_contributed: number;
  /** Sums over entries that have a value; null when none do. */
  total_market_value?: number | null;
  total_unrealized_pl?: number | null;
  generated_at: string;
}
