/**
 * Investment Service - Extends BaseCrudService following ISP pattern
 * Provides CRUD operations for Investment entities
 *
 * Implements ICrudService<Investment> through BaseCrudService inheritance
 * @see BaseCrudService for available operations
 */

import { Injectable } from '@angular/core';
import { BaseCrudService } from '@core_services/base-crud.service';
import { HttpClient } from '@angular/common/http';
import { InvestmentBase as Investment } from '@investments_models/InvestmentBase';

@Injectable({
  providedIn: 'root'
})
export class InvestmentService extends BaseCrudService<Investment> {
  /**
   * Initialize the service with HTTP client and API endpoint
   * @param http Angular HttpClient for making HTTP requests
   */
  constructor(protected override http: HttpClient) {
    super(http, 'investments');
  }
}
