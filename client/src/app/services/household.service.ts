// household.service.ts
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BaseCrudService } from './base-crud.service';
import { HouseholdBase as Household } from '../models/HouseholdBase';

@Injectable({
  providedIn: 'root'
})
export class HouseholdService extends BaseCrudService<Household> {
  constructor(protected override http: HttpClient) {
    super(http, 'households');
  }
}
