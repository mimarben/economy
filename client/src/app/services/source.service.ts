import { Injectable } from '@angular/core';
import { BaseCrudService } from './base-crud.service';
import { HttpClient } from '@angular/common/http';
import { SourceBase as Source } from '../models/SourceBase';
@Injectable({
  providedIn: 'root'
})
export class SourceService extends BaseCrudService<Source> {
constructor(protected override http: HttpClient) {
    super(http, 'sources');
  }
}
