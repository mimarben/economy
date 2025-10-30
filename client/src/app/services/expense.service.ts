import { Injectable } from '@angular/core';
import { BaseCrudService } from './base-crud.service';
import { HttpClient } from '@angular/common/http';
import { ExpenseBase as Expense  } from '@models/ExpenseBase';

@Injectable({
  providedIn: 'root'
})
export class ExpenseService extends BaseCrudService<Expense> {
  constructor(protected override http: HttpClient) {
    super(http, 'expenses');
  }
}
