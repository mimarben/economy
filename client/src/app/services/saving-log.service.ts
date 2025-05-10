import { Injectable } from '@angular/core';
import { BaseCrudService } from './base-crud.service';
import { HttpClient } from '@angular/common/http';
import { SavingLogBase as SavingLog } from '../models/SavingLogBase';
@Injectable({
  providedIn: 'root'
})
export class SavingLogService extends BaseCrudService<SavingLog> {
constructor(protected override http: HttpClient) {
    super(http, 'savings_logs');
  }
}
