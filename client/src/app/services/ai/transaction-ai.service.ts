import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '@env/environment';
import { ApiResponse } from '@core_models/apiResponse';

export interface ClassifyRequest {
  id: number;
  type: 'income' | 'expense' | 'investment';
  description: string;
  amount: number;
  bank_id?: string;
  bank_name?: string;
  import_format?: string;
}

export interface ClassifyResult {
  id: number;
  category_id: { id: number; name: string; description?: string } | null;
}

@Injectable({
  providedIn: 'root',
})
export class TransactionAiService {
  private baseUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  classify(transactions: ClassifyRequest[]): Observable<ApiResponse<ClassifyResult[]>> {
    const headers = new HttpHeaders(environment.headers);
    return this.http.post<ApiResponse<ClassifyResult[]>>(
      `${this.baseUrl}/transactions/classify`,
      transactions,
      { headers }
    );
  }
}
