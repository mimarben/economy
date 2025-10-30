import { Injectable } from '@angular/core';
import { BaseCrudService } from './base-crud.service';
import { HttpClient } from '@angular/common/http';
import { InvestmentLogBase as InvestmentLog } from '@models/InvestmentLogBase';
@Injectable({
  providedIn: 'root'
})
export class InvestmentLogService extends BaseCrudService<InvestmentLog> {
constructor(protected override http: HttpClient) {
    super(http, 'investments_logs');
  }
}
