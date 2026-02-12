/**
 * Account Service - Extends BaseCrudService following ISP pattern
 * Provides CRUD operations for Account entities
 *
 * Implements ICrudService<Account> through BaseCrudService inheritance
 * @see BaseCrudService for available operations
 */

import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { AccountBase as Account } from '../models/AccountBase';
import { BaseCrudService } from './base-crud.service';

@Injectable({
  providedIn: 'root'
})
export class AccountService extends BaseCrudService<Account> {
  /**
   * Initialize the service with HTTP client and API endpoint
   * @param http Angular HttpClient for making HTTP requests
   */
  constructor(protected override http: HttpClient) {
    super(http, 'accounts');
  }
}
