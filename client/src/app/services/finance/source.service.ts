/**
 * Source Service - Extends BaseCrudService following ISP pattern
 * Provides CRUD operations for Source entities
 *
 * Implements ICrudService<Source> through BaseCrudService inheritance
 * @see BaseCrudService for available operations
 */

import { Injectable } from '@angular/core';
import { BaseCrudService } from '@core_services/base-crud.service';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '@env/environment';
import { ApiResponse } from '@core_models/apiResponse';
import { SourceBase as Source } from '@finance_models/SourceBase';

@Injectable({
  providedIn: 'root'
})
export class SourceService extends BaseCrudService<Source> {
  /**
   * Initialize the service with HTTP client and API endpoint
   * @param http Angular HttpClient for making HTTP requests
   */
  constructor(protected override http: HttpClient) {
    super(http, 'sources');
  }

  /**
   * Suggest a source based on category or transaction type.
   * Backend endpoint is optional; fallback to first active source if not available.
   */
  suggestSource(categoryId: number, transactionType: 'expense' | 'income' | 'investment'): Observable<ApiResponse<Source>> {
    return this.http.get<ApiResponse<Source>>(`${environment.apiUrl}/sources/suggest?category_id=${categoryId}&type=${transactionType}`);
  }
}
