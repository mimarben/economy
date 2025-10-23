import { Injectable } from '@angular/core';
import { BaseCrudService } from './base-crud.service';
import { HttpClient } from '@angular/common/http';
import { SavingBase as Saving } from '../models/SavingBase';

@Injectable({
  providedIn: 'root'
})
export class SavingService extends BaseCrudService<Saving> {
constructor(protected override http: HttpClient) {
    super(http, 'savings');
  }
}
