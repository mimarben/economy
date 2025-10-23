// base-crud.service.ts
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { ApiResponse } from '../models/apiResponse';

@Injectable({ providedIn: 'root' })
export abstract class BaseCrudService<T> {
  protected baseUrl = environment.apiUrl;
  protected endpoint: string;
  constructor(protected http: HttpClient,
    endpoint: string) {
      this.endpoint = endpoint;
    }
  protected getUrl(): string {
    return `${this.baseUrl}/${this.endpoint}`;
  }

  protected getHeaders(): HttpHeaders {
    return new HttpHeaders(environment.headers);
  }

  getAll(): Observable<ApiResponse<T[]>> {
    return this.http.get<ApiResponse<T[]>>(this.getUrl());
  }

  getById(id: number): Observable<ApiResponse<T>> {
    return this.http.get<ApiResponse<T>>(`${this.getUrl()}/${id}`);
  }

  create(item: T): Observable<ApiResponse<T>> {
    return this.http.post<ApiResponse<T>>(this.getUrl(), item, { headers: this.getHeaders() });
  }

  update(id: number, item: T): Observable<ApiResponse<T>> {
    return this.http.patch<ApiResponse<T>>(`${this.getUrl()}/${id}`, item, { headers: this.getHeaders() });
  }

  delete(id: number): Observable<ApiResponse<any>> {
    return this.http.delete<ApiResponse<any>>(`${this.getUrl()}/${id}`, { headers: this.getHeaders() });
  }
}
