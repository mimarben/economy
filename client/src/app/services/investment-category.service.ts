import { Injectable } from '@angular/core';
import { BaseCrudService } from './base-crud.service';
import { HttpClient } from '@angular/common/http';
import { InvestmentCategoryBase as InvestmentCategory } from '../models/InvestmentCategoryBase';

@Injectable({
  providedIn: 'root'
})
export class InvestmentCategoryService extends BaseCrudService<InvestmentCategory> {
  constructor(protected override http: HttpClient) {
    super(http, 'investments_categories');
  }
}
