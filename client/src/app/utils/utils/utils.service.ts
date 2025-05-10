import { Injectable } from '@angular/core';
import moment from 'moment';
import _ from 'lodash';

@Injectable({
  providedIn: 'root'
})
export class UtilsService {
  readonly moment = moment;
  readonly lodash = _;
}