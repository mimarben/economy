import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BaseCrudService } from './base-crud.service';
import { HouseholdMemberBase as HouseHoldMember } from '../models/HouseholdMemberBase';

@Injectable({
  providedIn: 'root'
})
export class HouseholdMemberService extends BaseCrudService<HouseHoldMember> {
  constructor(protected override http: HttpClient) {
    super(http, 'households_members');
  }
}
