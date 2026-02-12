/**
 * Source Service - Extends BaseCrudService following ISP pattern
 * Provides CRUD operations for Source entities
 *
 * Implements ICrudService<Source> through BaseCrudService inheritance
 * @see BaseCrudService for available operations
 */

import { Injectable } from '@angular/core';
import { BaseCrudService } from './base-crud.service';
import { HttpClient } from '@angular/common/http';
import { SourceBase as Source } from '../models/SourceBase';

@Injectable({
  providedIn: 'root'
})
export class SourceService extends BaseCrudService<Source> {
  /**
   * Initialize the service with HTTP client and API endpoint
   * @param http Angular HttpClient for making HTTP requests
   */
  constructor(protected override http: HttpClient) {
    super(http, 'sources');
  }
}
