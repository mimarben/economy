/**
 * Household Service - Extends BaseCrudService following ISP pattern
 * Provides CRUD operations for Household entities
 *
 * Implements ICrudService<Household> through BaseCrudService inheritance
 * @see BaseCrudService for available operations
 */

import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BaseCrudService } from '@core_services/base-crud.service';
import { HouseholdBase as Household } from '@households_models/HouseholdBase';

@Injectable({
  providedIn: 'root'
})
export class HouseholdService extends BaseCrudService<Household> {
  /**
   * Initialize the service with HTTP client and API endpoint
   * @param http Angular HttpClient for making HTTP requests
   */
  constructor(protected override http: HttpClient) {
    super(http, 'households');
  }
}
