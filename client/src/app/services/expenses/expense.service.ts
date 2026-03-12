/**
 * Expense Service - Extends BaseCrudService following ISP pattern
 * Provides CRUD operations for Expense entities
 *
 * Implements ICrudService<Expense> through BaseCrudService inheritance
 * @see BaseCrudService for available operations
 */

import { Injectable } from '@angular/core';
import { BaseCrudService } from '@core_services/base-crud.service';
import { HttpClient } from '@angular/common/http';
import { ExpenseBase as Expense } from '@expenses_models/ExpenseBase';

@Injectable({
  providedIn: 'root'
})
export class ExpenseService extends BaseCrudService<Expense> {
  /**
   * Initialize the service with HTTP client and API endpoint
   * @param http Angular HttpClient for making HTTP requests
   */
  constructor(protected override http: HttpClient) {
    super(http, 'expenses');
  }
}
