/**
 * Income Service - Extends BaseCrudService following ISP pattern
 * Provides CRUD operations for Income entities
 *
 * Implements ICrudService<Income> through BaseCrudService inheritance
 * @see BaseCrudService for available operations
 */

import { Injectable } from '@angular/core';
import { BaseCrudService } from '@core_services/base-crud.service';
import { HttpClient } from '@angular/common/http';
import { IncomeBase as Income } from '@incomes_models/IncomeBase';

@Injectable({
  providedIn: 'root'
})
export class IncomeService extends BaseCrudService<Income> {
  /**
   * Initialize the service with HTTP client and API endpoint
   * @param http Angular HttpClient for making HTTP requests
   */
  constructor(protected override http: HttpClient) {
    super(http, 'incomes');
  }
}
