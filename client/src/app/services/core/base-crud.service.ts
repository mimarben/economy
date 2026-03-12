/**
 * Base CRUD Service implementing segregated ISP interfaces
 * Provides generic CRUD operations for all entities following ISP pattern
 */

import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '@env/environment';
import { ApiResponse } from '@core_models/apiResponse';
import { WithAuditFields } from '@core_models/auditable';
import { ICrudService } from '@core_services/interfaces';

@Injectable({ providedIn: 'root' })
export abstract class BaseCrudService<T> implements ICrudService<T> {
  protected baseUrl = environment.apiUrl;
  protected endpoint: string;

  constructor(protected http: HttpClient, endpoint: string) {
    this.endpoint = endpoint;
  }

  /**
   * Get the full API URL for this endpoint
   */
  protected getUrl(): string {
    return `${this.baseUrl}/${this.endpoint}`;
  }

  /**
   * Get HTTP headers for requests
   * Injected via HttpInterceptor in practice
   */
  protected getHeaders(): HttpHeaders {
    return new HttpHeaders(environment.headers);
  }

  /**
   * IReadService: Get all items of type T
   */
  getAll(): Observable<ApiResponse<WithAuditFields<T>[]>> {
    return this.http.get<ApiResponse<WithAuditFields<T>[]>>(this.getUrl());
  }

  /**
   * IReadService: Get a single item by ID
   */
  getById(id: number): Observable<ApiResponse<WithAuditFields<T>>> {
    return this.http.get<ApiResponse<WithAuditFields<T>>>(`${this.getUrl()}/${id}`);
  }

  /**
   * ICreateService: Create a new item
   */
  create(item: T): Observable<ApiResponse<WithAuditFields<T>>> {
    return this.http.post<ApiResponse<WithAuditFields<T>>>(this.getUrl(), item, {
      headers: this.getHeaders(),
    });
  }

  /**
   * IUpdateService: Update an existing item
   */
  update(id: number, item: T): Observable<ApiResponse<WithAuditFields<T>>> {
    return this.http.patch<ApiResponse<WithAuditFields<T>>>(`${this.getUrl()}/${id}`, item, {
      headers: this.getHeaders(),
    });
  }

  /**
   * IDeleteService: Delete an item
   */
  delete(id: number): Observable<ApiResponse<any>> {
    return this.http.delete<ApiResponse<any>>(`${this.getUrl()}/${id}`, {
      headers: this.getHeaders(),
    });
  }
}
