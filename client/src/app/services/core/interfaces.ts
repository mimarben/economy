/**
 * Segregated Service Interfaces following Interface Segregation Principle (ISP)
 * Each interface represents a single responsibility
 */

import { Observable } from 'rxjs';
import { ApiResponse } from '@core_models/apiResponse';

/**
 * Interface for read operations only
 * Used by components that only need to retrieve data
 */
export interface IReadService<T> {
  getAll(): Observable<ApiResponse<T[]>>;
  getById(id: number): Observable<ApiResponse<T>>;
}

/**
 * Interface for create operations only
 * Used by components that only need to create data
 */
export interface ICreateService<T> {
  create(item: T): Observable<ApiResponse<T>>;
}

/**
 * Interface for update operations only
 * Used by components that only need to update data
 */
export interface IUpdateService<T> {
  update(id: number, item: T): Observable<ApiResponse<T>>;
}

/**
 * Interface for delete operations only
 * Used by components that only need to delete data
 */
export interface IDeleteService {
  delete(id: number): Observable<ApiResponse<any>>;
}

/**
 * Combined CRUD interface for services that need all operations
 */
export interface ICrudService<T>
  extends IReadService<T>,
    ICreateService<T>,
    IUpdateService<T>,
    IDeleteService {}
