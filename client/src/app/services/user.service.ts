/**
 * User Service - Extends BaseCrudService following ISP pattern
 * Provides CRUD operations for User entities
 */

import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BaseCrudService } from './base-crud.service';
import { UserBase as User } from '../models/UserBase';

@Injectable({
  providedIn: 'root',
})
export class UserService extends BaseCrudService<User> {
  constructor(protected override http: HttpClient) {
    super(http, 'users');
  }

  /**
   * Get all users
   * Inherited from IReadService via BaseCrudService
   */

  /**
   * Get user by ID
   * Inherited from IReadService via BaseCrudService
   */

  /**
   * Create new user
   * Inherited from ICreateService via BaseCrudService
   */

  /**
   * Update user
   * Inherited from IUpdateService via BaseCrudService
   */

  /**
   * Delete user
   * Inherited from IDeleteService via BaseCrudService
   */
}
