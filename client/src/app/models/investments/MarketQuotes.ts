/* eslint-disable */
/**
 * Models for market quotes and the investments dashboard.
 * Hand-written (not schema-generated): these endpoints return computed
 * payloads (joins of contributions + cached quotes), not CRUD entities.
 */

/** Quote status: ok = fresh, stale = cached older than TTL, unavailable = no data. */
export type QuoteStatus = 'ok' | 'stale' | 'unavailable';

/** Asset class / categoría del instrumento */
export type AssetClass = 'ETF' | 'FUND' | 'STOCK' | 'CRYPTO' | 'BOND' | 'MANAGED_PORTFOLIO' | 'OTHER';

/** Estado de la posición: ACTIVE o CLOSED */
export type PositionStatus = 'ACTIVE' | 'CLOSED';

/** Tipo de precio para frescura de cotización */
export type PriceType = 'EOD' | 'DELAYED' | 'REAL_TIME' | 'NAV';

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
  category?: AssetClass | null;  // NUEVO: categoría del instrumento
  asset_class?: AssetClass | null;  // NUEVO: clase de activo (sinónimo de category)
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
  position_status?: PositionStatus;  // NUEVO: estado de la posición (ACTIVE/CLOSED)
  last_log_date?: string | null;  // NUEVO: fecha/hora del último log/valoración
  price_type?: PriceType | null;  // NUEVO: tipo de precio (EOD, DELAYED, REAL_TIME, NAV)
  last_quote_source?: string | null;  // NUEVO: fuente de la última cotización
}

/** Inversión sin ISIN (cartera gestionada, cripto, efectivo): valorada a mano. */
export interface UnquotedEntry {
  investment_id: number;
  name: string;
  currency?: string | null;
  total_contributed: number;
  last_contribution_date?: string | null;
  /** Units held from the latest investment log; null = never logged. */
  units?: number | null;
  /** Last hand-recorded valuation. */
  reported_value?: number | null;
  /** reported_value (manual valuation). */
  value?: number | null;
  /** reported_value - total_contributed. */
  unrealized_pl?: number | null;
  unrealized_pl_pct?: number | null;
  last_log_date?: string | null;
}

export interface InvestmentsDashboard {
  entries: DashboardEntry[];
  /** Investments without ISIN, valued manually (managed portfolios, crypto). */
  unquoted_entries?: UnquotedEntry[];
  without_isin_count: number;
  without_isin_amount: number;
  total_contributed: number;
  /** Sums over entries that have a value; null when none do. */
  total_market_value?: number | null;
  total_unrealized_pl?: number | null;
  /** Sum of hand-recorded values of unquoted entries; null when none. */
  total_reported_value?: number | null;
  /** Sum of unrealized_pl of unquoted entries (manual valuation). */
  total_reported_pl?: number | null;
  generated_at: string;
}

/**
 * Resultado de búsqueda universal de instrumentos
 */
export interface InstrumentSearchResult {
  isin?: string | null;
  symbol?: string | null;
  name: string;
  asset_class?: AssetClass | null;
  category?: string | null;
  currency?: string | null;
  exchange?: string | null;
  provider?: string | null;
  description?: string | null;
}

/**
 * Petición de búsqueda universal
 */
export interface SearchRequest {
  query: string;
  limit?: number;
}

/**
 * Respuesta de búsqueda universal
 */
export interface SearchResponse {
  results: InstrumentSearchResult[];
  total: number;
}
