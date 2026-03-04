/**
 * Bank Service - Extends BaseCrudService following ISP pattern
 * Provides CRUD operations for Bank entities
 */

import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BaseCrudService } from '@core_services/base-crud.service';
import { BankBase as Bank } from '@finance_models/BankBase';
import { Observable } from 'rxjs';
import { ApiResponse } from '@core_models/apiResponse';

@Injectable({
  providedIn: 'root',
})
export class BankService extends BaseCrudService<Bank> {
  constructor(protected override http: HttpClient) {
    super(http, 'banks');
  }

  /**
   * All CRUD operations inherited from BaseCrudService:
   * - getAll()
   * - getById(id)
   * - create(item)
   * - update(id, item)
   * - delete(id)
   */

  /**
   * Alias for getAll() - Get all banks
   */
  getBanks(): Observable<ApiResponse<Bank[]>> {
    return this.getAll();
  }

  /**
   * Alias for create() - Create a new bank
   */
  createBank(bank: Bank): Observable<ApiResponse<Bank>> {
    return this.create(bank);
  }

  /**
   * Alias for update() - Update an existing bank
   */
  updateBank(id: number, bank: Bank): Observable<ApiResponse<Bank>> {
    return this.update(id, bank);
  }
}
