import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '@env/environment';
import { ApiResponse } from '@core_models/apiResponse';
import { ClassifyPayload, ClassifyResult } from '@import_models/classify-request-ai';


@Injectable({
  providedIn: 'root',
})
export class TransactionAiService {
  private baseUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  publicclassify(payload: ClassifyPayload): Observable<ApiResponse<ClassifyResult[]>> {
    const headers = new HttpHeaders(environment.headers);
    return this.http.post<ApiResponse<ClassifyResult[]>>(
      `${this.baseUrl}/transactions/classify`,
      payload,
      { headers }
    );
  }
}
