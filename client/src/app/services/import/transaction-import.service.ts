import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '@env/environment';
import { ApiResponse } from '@app/models/core/APIResponse';

export interface BulkImportPayload {
  expenses: any[];
  incomes: any[];
}

@Injectable({
  providedIn: 'root'
})
export class TransactionImportService {
  private readonly baseUrl = environment.apiUrl + '/imports/transactions/bulk';

  constructor(private http: HttpClient) {}

  importAtomic(payload: BulkImportPayload): Observable<ApiResponse<any>> {
    return this.http.post<ApiResponse<any>>(this.baseUrl, payload);
  }
}
