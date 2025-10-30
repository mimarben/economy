import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { AccountBase as Account  } from '../models/AccountBase';
import { BaseCrudService } from './base-crud.service';

@Injectable({
  providedIn: 'root'
})


export class AccountService extends BaseCrudService<Account>{
  constructor(protected override http: HttpClient) {
    super(http, 'accounts');
  }


}
