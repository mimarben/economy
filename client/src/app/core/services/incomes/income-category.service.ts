/**
 * Income Category Service - Extends BaseCrudService following ISP pattern
 * Provides CRUD operations for IncomeCategory entities
 *
 * Implements ICrudService<IncomeCategory> through BaseCrudService inheritance
 * @see BaseCrudService for available operations
 */

import { Injectable } from '@angular/core';
import { BaseCrudService } from '@core_services/base-crud.service';
import { HttpClient } from '@angular/common/http';
import { IncomeCategoryBase as IncomeCategory } from '@incomes_models/IncomeCategoryBase';

@Injectable({
  providedIn: 'root'
})
export class IncomeCategoryService extends BaseCrudService<IncomeCategory> {
  /**
   * Initialize the service with HTTP client and API endpoint
   * @param http Angular HttpClient for making HTTP requests
   */
  constructor(protected override http: HttpClient) {
    super(http, 'income_categories');
  }
}
