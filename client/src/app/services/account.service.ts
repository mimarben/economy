import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { AccountBase as Account  } from '../models/AccountBase';
import { ApiResponse } from '../models/apiResponse';

@Injectable({
  providedIn: 'root'
})


export class AccountService {
  private apiUrl = environment.apiUrl;
  constructor(private http: HttpClient) {
  }

  private getHeaders(): HttpHeaders {
    return new HttpHeaders(environment.headers);
  }
getAccounts(): Observable<ApiResponse<Account[]>> {
  return this.http.get<ApiResponse<Account[]>>(`${this.apiUrl}/accounts`);
}
getAccountById(id: number): Observable<ApiResponse<Account>> {
  return this.http.get<ApiResponse<Account>>(`${this.apiUrl}/accounts/${id}`);
}
createAccount(account: Account): Observable<ApiResponse<Account>> {
  return this.http.post<ApiResponse<Account>>(`${this.apiUrl}/accounts`, account, { headers: this.getHeaders() } );
}
updateAccount(id: number, account: Account): Observable<ApiResponse<Account>> {
  return this.http.patch<ApiResponse<Account>>(`${this.apiUrl}/accounts/${id}`, account, { headers: this.getHeaders() });
}

}
