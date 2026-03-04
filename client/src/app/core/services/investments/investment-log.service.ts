/**
 * Investment Log Service - Extends BaseCrudService following ISP pattern
 * Provides CRUD operations for InvestmentLog entities
 *
 * Implements ICrudService<InvestmentLog> through BaseCrudService inheritance
 * @see BaseCrudService for available operations
 */

import { Injectable } from '@angular/core';
import { BaseCrudService } from '@core_services/base-crud.service';
import { HttpClient } from '@angular/common/http';
import { InvestmentLogBase as InvestmentLog } from '@investments_models/InvestmentLogBase';

@Injectable({
  providedIn: 'root'
})
export class InvestmentLogService extends BaseCrudService<InvestmentLog> {
  /**
   * Initialize the service with HTTP client and API endpoint
   * @param http Angular HttpClient for making HTTP requests
   */
  constructor(protected override http: HttpClient) {
    super(http, 'investments_logs');
  }
}
