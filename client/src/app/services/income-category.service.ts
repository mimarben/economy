import { Injectable, model } from '@angular/core';
import { BaseCrudService } from './base-crud.service';
import { HttpClient } from '@angular/common/http';
import { IncomeCategoryBase as IncomeCategory } from '@models/IncomeCategoryBase';

@Injectable({
  providedIn: 'root'
})
export class IncomeCategoryService extends BaseCrudService<IncomeCategory> {
  constructor(protected override http: HttpClient) {
    super(http, 'income_categories');
  }
}
