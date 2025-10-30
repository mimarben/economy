import { Injectable } from '@angular/core';
import { BaseCrudService } from './base-crud.service';
import { HttpClient } from '@angular/common/http';
import { IncomeBase as Income  } from '@models/IncomeBase';

@Injectable({
  providedIn: 'root'
})
export class IncomeService extends BaseCrudService<Income> {
  constructor(protected override http: HttpClient) {
    super(http, 'incomes');
  }
}
