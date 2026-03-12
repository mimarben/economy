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
  // ... añade todas las que encuentres ...
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
    // ... mapea el resto aquí ...
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
    // NOTA: date-fns usa 'dd', 'MM', 'yyyy' (minúsculas)
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

    // Si ya es Date
    if (isDate(value)) return value as Date;

    // Si es string o number
    if (typeof value === 'string' || typeof value === 'number') {
      const d = new Date(value);
      return isValid(d) ? d : null;
    }

    return null; // cualquier otro tipo no válido
  }
  }
