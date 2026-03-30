import { Injectable } from '@angular/core';
//import moment from 'moment';
import {
  format,
  parse,
  isValid,
  startOfDay,
  isDate
} from 'date-fns';
import {
  cloneDeep,
  isEmpty,
  map,
  filter,
  // Comment translated to English.
} from 'lodash-es';

@Injectable({
  providedIn: 'root'
})
export class UtilsService {
  readonly _ = {
    cloneDeep: cloneDeep,
    isEmpty: isEmpty,
    map: map,
    filter: filter,
    // Comment translated to English.
  };
  //readonly moment = moment;
  // Internal helper to convert MomentInput (Date, string, number) to a Date object,
  // since date-fns works primarily with native Date objects.
  public getDate(date: Date | string | number | null | undefined): Date | null {
      if (!date) return null;
      if (isDate(date)) return date as Date;
      // Handle string or number input by creating a Date object
      const d = new Date(date);
      return isValid(d) ? d : null;
  }
  formatDateShortStr(date: Date | string | number | null | undefined): string {
    const d = this.getDate(date);
    if (!d) return '';
    // Comment translated to English.
    return format(d, 'dd-MM-yyyy');
  }
  // Uses 'date-fns/startOfDay' and returns a native Date
  formatDateShort(date: Date | string | number | null | undefined): Date | null {
    const d = this.getDate(date);
    if (!d) return null;
    return startOfDay(d);
  }
  // Uses 'date-fns/format' with time
  formatDateLong(date: Date | string | number | null | undefined): string {
    const d = this.getDate(date);
    if (!d) return '';
    return format(d, 'dd-MM-yyyy HH:mm:ss');
  }

  // Parse a string in 'DD-MM-YYYY' format to a native Date object
  // Uses 'date-fns/parse'
  parseToDate(dateString: string): Date | null {
    if (!dateString) return null;

    // Parse the string using the expected format 'dd-MM-yyyy', and a dummy reference date (new Date())
    const d = parse(dateString, 'dd-MM-yyyy', new Date());

    return isValid(d) ? d : null;
  }
  public parseToSafeDate(value: unknown): Date | null {
    if (!value) return null;

    // If value is already a Date
    if (isDate(value)) return value as Date;

    // If value is a string or number
    if (typeof value === 'string' || typeof value === 'number') {
      const d = new Date(value);
      return isValid(d) ? d : null;
    }

    return null; // any other type is invalid
  }
  public normalize(text: string): string {
  return text
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "") // remove accents
    .replace(/[^a-z0-9 ]/g, "") // remove symbols
    .trim();
  }
  public parseAmount(value: any): number {
    if (value == null || value === '' || value === undefined) return 0;
    if (typeof value === 'number') return value;

    let str = String(value)
      .trim()
      .replace(/[€\s]/g, '')
      .replace('−', '-');

    const lastDot = str.lastIndexOf('.');
    const lastComma = str.lastIndexOf(',');

    if (lastComma > lastDot) {
      // European number format: 1.501,70
      str = str.replace(/\./g, '').replace(',', '.');
    } else if (lastDot > lastComma) {
      // English number format: 1,501.70
      str = str.replace(/,/g, '');
    }
    const num = Number(str);
    if (Number.isNaN(num)) return 0;
    //console.log("Valor raw:", value, "parsed:", num);
    return num;
  }

  }
