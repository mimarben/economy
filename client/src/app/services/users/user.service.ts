import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BaseCrudService } from '@core_services/base-crud.service';
import { UserBase as User } from '@users_models/UserBase';
import { Observable } from 'rxjs';
import { ApiResponse } from '@core_models/apiResponse';

@Injectable({
  providedIn: 'root',
})
export class UserService extends BaseCrudService<User> {
  constructor(protected override http: HttpClient) {
    super(http, 'users');
  }

  /**
   * Alias for getAll() - Get all users
   */
  getUsers(): Observable<ApiResponse<User[]>> {
    return this.getAll();
  }

  /**
   * Alias for create() - Create a new user
   */
  createUser(user: User): Observable<ApiResponse<User>> {
    return this.create(user);
  }

  /**
   * Alias for update() - Update an existing user
   */
  updateUser(id: number, user: User): Observable<ApiResponse<User>> {
    return this.update(id, user);
  }
}
