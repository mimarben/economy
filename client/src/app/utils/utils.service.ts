import { Injectable } from '@angular/core';
import moment from 'moment';
import _ from 'lodash';

@Injectable({
  providedIn: 'root'
})
export class UtilsService {
  readonly moment = moment;
  readonly lodash = _;

    formatDateShortStr(date: moment.MomentInput): string {
      return moment(date).format('DD-MM-YYYY');
    }

    formatDateShortDate(date: moment.MomentInput): Date | null {
      if (!date) return null;
      const m = moment(date).startOf('day');
      return m.isValid() ? m.toDate() : null;
    }

    formatDateLong(date: moment.MomentInput): string {
      return moment(date).format('DD-MM-YYYY HH:mm:ss');
    }
    // Parse a string in 'DD-MM-YYYY' format to a Moment object
    parseToMoment(dateString: string): moment.Moment | null {
      if (!dateString) return null;
      const m = moment(dateString, 'DD-MM-YYYY', true);
      return m.isValid() ? m : null;
    }

    // Parse a string in 'DD-MM-YYYY' format to a native Date object
    parseToDate(dateString: string): Date | null {
      if (!dateString) return null;
      const [day, month, year] = dateString.split('-').map(Number);
      const d = new Date(year, month - 1, day);
      return isNaN(d.getTime()) ? null : d;
    }
  }
