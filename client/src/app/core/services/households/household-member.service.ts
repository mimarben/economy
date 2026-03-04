/**
 * Household Member Service - Extends BaseCrudService following ISP pattern
 * Provides CRUD operations for HouseholdMember entities
 *
 * Implements ICrudService<HouseholdMember> through BaseCrudService inheritance
 * @see BaseCrudService for available operations
 */

import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BaseCrudService } from '@core_services/base-crud.service';
import { HouseholdMemberBase as HouseholdMember } from '@households_models/HouseholdMemberBase';

@Injectable({
  providedIn: 'root'
})
export class HouseholdMemberService extends BaseCrudService<HouseholdMember> {
  /**
   * Initialize the service with HTTP client and API endpoint
   * @param http Angular HttpClient for making HTTP requests
   */
  constructor(protected override http: HttpClient) {
    super(http, 'households_members');
  }
}
