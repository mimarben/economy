import { BaseCrudService } from '@core_services/base-crud.service';
import { HttpClient } from '@angular/common/http';
import { ImportOriginBase as ImportOrigin } from '@app/models/import/import-originBase';
import { ImportProfileBase as ImportProfile } from '@app/models/import/import-profileBase';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs/internal/Observable';
import { ApiResponse } from '@app/models/core/APIResponse';

// Create types with optional id for create operations
export type ImportOriginCreate = Omit<ImportOrigin, 'id'>;
export type ImportProfileCreate = Omit<ImportProfile, 'id'>;

@Injectable({
  providedIn: 'root',
})
export class ImportOriginsService extends BaseCrudService<ImportOrigin> {
  constructor(protected override http: HttpClient) {
    super(http, 'import-origins');
  }

  /**
   * Alias for getAll() - Get all import origins
   */
  getOrigins(): Observable<ApiResponse<ImportOrigin[]>> {
    return this.getAll();
  }

  /**
   * Override create to accept ImportOriginCreate (without id)
   */
  createOrigin(origin: ImportOriginCreate): Observable<ApiResponse<ImportOrigin>> {
    return super.create(origin as ImportOrigin);
  }

  /**
   * Alias for update() - Update an existing import origin
   */
  updateOrigin(id: number, origin: ImportOrigin): Observable<ApiResponse<ImportOrigin>> {
    return this.update(id, origin);
  }

  /**
   * Alias for delete() - Delete an import origin
   */
  deleteOrigin(id: number): Observable<ApiResponse<any>> {
    return this.delete(id);
  }
}

@Injectable({
  providedIn: 'root',
})
export class ImportProfilesService extends BaseCrudService<ImportProfile> {
  constructor(protected override http: HttpClient) {
    super(http, 'import-profiles');
  }

  /**
   * Alias for getAll() - Get all import profiles
   */
  getProfiles(): Observable<ApiResponse<ImportProfile[]>> {
    return this.getAll();
  }

  /**
   * Alias for getById() - Get a single import profile by ID
   */
  getProfile(id: number): Observable<ApiResponse<ImportProfile>> {
    return this.getById(id);
  }

  /**
   * Override create to accept ImportProfileCreate (without id)
   */
  createProfile(profile: ImportProfileCreate): Observable<ApiResponse<ImportProfile>> {
    return super.create(profile as ImportProfile);
  }

  /**
   * Alias for update() - Update an existing import profile
   */
  updateProfile(id: number, profile: ImportProfile): Observable<ApiResponse<ImportProfile>> {
    return this.update(id, profile);
  }

  /**
   * Alias for delete() - Delete an import profile
   */
  deleteProfile(id: number): Observable<ApiResponse<any>> {
    return this.delete(id);
  }
}