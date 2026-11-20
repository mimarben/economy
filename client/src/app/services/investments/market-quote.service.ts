/**
 * Market Quote Service - read-only access to market data endpoints
 * (quotes cache + investments dashboard). Not a CRUD entity, so it does
 * not extend BaseCrudService.
 */

import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '@env/environment';
import { ApiResponse } from '@app/models/core/APIResponse';
import { InvestmentsDashboard, MarketQuote, SearchRequest, SearchResponse } from '@investments_models/MarketQuotes';

@Injectable({
  providedIn: 'root'
})
export class MarketQuoteService {
  constructor(protected http: HttpClient) {}

  /** Portfolio grouped by ISIN with its market quote. */
  getDashboard(forceRefresh = false): Observable<ApiResponse<InvestmentsDashboard>> {
    const params = forceRefresh ? new HttpParams().set('refresh', 'true') : undefined;
    return this.http.get<ApiResponse<InvestmentsDashboard>>(
      `${environment.apiUrl}/investments/dashboard`,
      { params }
    );
  }

  /** Quotes for arbitrary ISINs (comma-free list). */
  getQuotes(isins: string[], forceRefresh = false): Observable<ApiResponse<MarketQuote[]>> {
    let params = new HttpParams().set('isins', isins.join(','));
    if (forceRefresh) {
      params = params.set('refresh', 'true');
    }
    return this.http.get<ApiResponse<MarketQuote[]>>(
      `${environment.apiUrl}/market/quotes`,
      { params }
    );
  }

  /**
   * Búsqueda universal contra /market/search del backend.
   * Selecciona obligatoriamente cuando hay varios resultados.
   */
  searchInstruments(query: string, limit: number = 20): Observable<ApiResponse<SearchResponse>> {
    const params = new HttpParams()
      .set('query', query)
      .set('limit', limit.toString());
    return this.http.get<ApiResponse<SearchResponse>>(
      `${environment.apiUrl}/market/search`,
      { params }
    );
  }

  /**
   * Obtiene el detalle de un instrumento por su ISIN o identificador.
   */
  getInstrumentDetail(isin: string): Observable<ApiResponse<MarketQuote>> {
    return this.http.get<ApiResponse<MarketQuote>>(
      `${environment.apiUrl}/market/search/${encodeURIComponent(isin)}`
    );
  }
}
