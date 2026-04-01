/**
 * Segregated Service Interfaces following Interface Segregation Principle (ISP)
 * Each interface represents a single responsibility
 */

import { Observable } from 'rxjs';
import { ApiResponse } from '@app/models/core/APIResponse';
import { WithAuditFields } from '@app/models/core/Auditable';

/**
 * Interface for read operations only
 * Used by components that only need to retrieve data
 */
export interface IReadService<T> {
  getAll(): Observable<ApiResponse<WithAuditFields<T>[]>>;
  getById(id: number): Observable<ApiResponse<WithAuditFields<T>>>;
}

/**
 * Interface for create operations only
 * Used by components that only need to create data
 */
export interface ICreateService<T> {
  create(item: T): Observable<ApiResponse<WithAuditFields<T>>>;
}

/**
 * Interface for update operations only
 * Used by components that only need to update data
 */
export interface IUpdateService<T> {
  update(id: number, item: T): Observable<ApiResponse<WithAuditFields<T>>>;
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
