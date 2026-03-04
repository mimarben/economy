/**
 * Saving Log Service - Extends BaseCrudService following ISP pattern
 * Provides CRUD operations for SavingLog entities
 *
 * Implements ICrudService<SavingLog> through BaseCrudService inheritance
 * @see BaseCrudService for available operations
 */

import { Injectable } from '@angular/core';
import { BaseCrudService } from '@core_services/base-crud.service';
import { HttpClient } from '@angular/common/http';
import { SavingLogBase as SavingLog } from '@savings_models/SavingLogBase';

@Injectable({
  providedIn: 'root'
})
export class SavingLogService extends BaseCrudService<SavingLog> {
  /**
   * Initialize the service with HTTP client and API endpoint
   * @param http Angular HttpClient for making HTTP requests
   */
  constructor(protected override http: HttpClient) {
    super(http, 'savings_logs');
  }
}
