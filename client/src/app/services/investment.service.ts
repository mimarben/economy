import { Injectable } from '@angular/core';
import { BaseCrudService } from './base-crud.service';
import { HttpClient } from '@angular/common/http';
import { InvestmentBase as Investment } from '../models/InvestmentBase';

@Injectable({
  providedIn: 'root'
})
export class InvestmentService extends BaseCrudService<Investment> {
  constructor(protected override http: HttpClient) {
    super(http, 'investments');
  }
}
