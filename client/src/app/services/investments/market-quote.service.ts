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
import { InvestmentsDashboard, MarketQuote } from '@investments_models/MarketQuotes';

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
}
