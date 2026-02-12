/**
 * Expense Category Service - Extends BaseCrudService following ISP pattern
 * Provides CRUD operations for ExpenseCategory entities
 *
 * Implements ICrudService<ExpenseCategory> through BaseCrudService inheritance
 * @see BaseCrudService for available operations
 */

import { Injectable } from '@angular/core';
import { BaseCrudService } from './base-crud.service';
import { HttpClient } from '@angular/common/http';
import { ExpenseCategoryBase as ExpenseCategory } from '@models/ExpenseCategoryBase';

@Injectable({
  providedIn: 'root'
})
export class ExpenseCategoryService extends BaseCrudService<ExpenseCategory> {
  /**
   * Initialize the service with HTTP client and API endpoint
   * @param http Angular HttpClient for making HTTP requests
   */
  constructor(protected override http: HttpClient) {
    super(http, 'expenses_categories');
  }
}
