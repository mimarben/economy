/**
 * Bank Service - Extends BaseCrudService following ISP pattern
 * Provides CRUD operations for Bank entities
 */

import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BaseCrudService } from './base-crud.service';
import { BankBase as Bank } from '../models/BankBase';

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
}
