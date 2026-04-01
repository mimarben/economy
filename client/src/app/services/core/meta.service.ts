
import { Observable } from 'rxjs';
import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { FormFieldConfig } from '@shared/generic-form/form-config';

@Injectable({
  providedIn: 'root',
})
export class MetaService {
  constructor(private http: HttpClient) {}

  getMeta(model: string): Observable<{ fields: FormFieldConfig[] }> {
    return this.http.get<{ fields: FormFieldConfig[] }>(`/api/meta/${model}`);
  }
}