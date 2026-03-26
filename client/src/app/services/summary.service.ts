import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '@env/environment';

export interface TotalByCategory {
  category_id: number;
  category_name: string;
  type: 'expense' | 'income' | 'investment';
  total: number;
}

export interface TotalOverTime {
  date: string;
  expense: number;
  income: number;
  investment: number;
  net: number;
}

export interface IncomeVsExpense {
  total_income: number;
  total_expense: number;
  net: number;
  count_transactions: number;
}

export interface SummaryResponse {
  period_start: string;
  period_end: string;
  totals_by_category: TotalByCategory[];
  totals_over_time: TotalOverTime[];
  income_vs_expense: IncomeVsExpense;
}

export type PeriodType = 'week' | 'month' | 'year' | 'custom';

@Injectable({
  providedIn: 'root'
})
export class SummaryService {
  private readonly apiUrl = `${environment.apiUrl}/summary`;

  constructor(private http: HttpClient) {}

  /**
   * Get summary for a custom date range.
   */
  getSummary(startDate: string, endDate: string): Observable<{ data: SummaryResponse }> {
    let params = new HttpParams()
      .set('start_date', startDate)
      .set('end_date', endDate);

    return this.http.get<{ data: SummaryResponse }>(this.apiUrl, { params });
  }

  /**
   * Get summary for current week.
   */
  getWeekSummary(): Observable<{ data: SummaryResponse }> {
    return this.http.get<{ data: SummaryResponse }>(`${this.apiUrl}/week`);
  }

  /**
   * Get summary for current month.
   */
  getMonthSummary(): Observable<{ data: SummaryResponse }> {
    return this.http.get<{ data: SummaryResponse }>(`${this.apiUrl}/month`);
  }

  /**
   * Get summary for current year.
   */
  getYearSummary(): Observable<{ data: SummaryResponse }> {
    return this.http.get<{ data: SummaryResponse }>(`${this.apiUrl}/year`);
  }
}
