import { Injectable, model } from '@angular/core';
import { BaseCrudService } from './base-crud.service';
import { HttpClient } from '@angular/common/http';
import { ExpenseCategoryBase as ExpenseCategory } from '@models/ExpenseCategoryBase';

@Injectable({
  providedIn: 'root'
})
export class ExpenseCategoryService extends BaseCrudService<ExpenseCategory> {
  constructor(protected override http: HttpClient) {
    super(http, 'expense_categories');
  }
}
