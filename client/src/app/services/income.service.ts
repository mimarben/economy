/**
 * Income Service - Extends BaseCrudService following ISP pattern
 * Provides CRUD operations for Income entities
 *
 * Implements ICrudService<Income> through BaseCrudService inheritance
 * @see BaseCrudService for available operations
 */

import { Injectable } from '@angular/core';
import { BaseCrudService } from './base-crud.service';
import { HttpClient } from '@angular/common/http';
import { IncomeBase as Income } from '@models/IncomeBase';

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
