import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, map } from 'rxjs';
import { environment } from '../../environments/environment';
import { BankBase as Bank, SelectBankOption  } from '../models/BankBase';
import { ApiResponse } from '../models/apiResponse';

@Injectable({
  providedIn: 'root'
})

export class BankService {
  private apiUrl = environment.apiUrl;
  constructor(private http: HttpClient) {
  }

  private getHeaders(): HttpHeaders {
    return new HttpHeaders(environment.headers);
  }
getBanks(): Observable<ApiResponse<Bank[]>> {
  return this.http.get<ApiResponse<Bank[]>>(`${this.apiUrl}/banks`);
}
getBankById(id: number): Observable<ApiResponse<Bank>> {
  return this.http.get<ApiResponse<Bank>>(`${this.apiUrl}/banks/${id}`);
}
createBank(user: Bank): Observable<ApiResponse<Bank>> {
  return this.http.post<ApiResponse<Bank>>(`${this.apiUrl}/banks`, user, { headers: this.getHeaders() } );
}
updateBank(id: number, user: Bank): Observable<ApiResponse<Bank>> {
  return this.http.patch<ApiResponse<Bank>>(`${this.apiUrl}/banks/${id}`, user, { headers: this.getHeaders() });
}

}
