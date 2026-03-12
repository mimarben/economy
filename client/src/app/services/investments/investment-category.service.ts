/**
 * Investment Category Service - Extends BaseCrudService following ISP pattern
 * Provides CRUD operations for InvestmentCategory entities
 *
 * Implements ICrudService<InvestmentCategory> through BaseCrudService inheritance
 * @see BaseCrudService for available operations
 */

import { Injectable } from '@angular/core';
import { BaseCrudService } from '@core_services/base-crud.service';
import { HttpClient } from '@angular/common/http';
import { InvestmentCategoryBase as InvestmentCategory } from '@investments_models/InvestmentCategoryBase';

@Injectable({
  providedIn: 'root'
})
export class InvestmentCategoryService extends BaseCrudService<InvestmentCategory> {
  /**
   * Initialize the service with HTTP client and API endpoint
   * @param http Angular HttpClient for making HTTP requests
   */
  constructor(protected override http: HttpClient) {
    super(http, 'investments_categories');
  }
}
