/**
 * Service for managing Category Rules via HTTP API.
 * 
 * Provides CRUD operations for categorization rules used in transaction import workflow.
 */

import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, BehaviorSubject } from 'rxjs';
import { tap, map } from 'rxjs/operators';
import { environment } from '../../../environments/environment';

export interface CategoryRule {
  id?: number;
  name: string;
  pattern: string;  // Regex pattern
  type: 'expense' | 'income' | 'investment';
  priority: number;
  is_active: boolean;
  category_id: number;
  created_at?: string;
  updated_at?: string;
}

export interface CategoryRuleUpdate {
  name?: string;
  pattern?: string;
  type?: 'expense' | 'income' | 'investment';
  priority?: number;
  is_active?: boolean;
  category_id?: number;
}

@Injectable({
  providedIn: 'root'
})
export class CategoryRuleService {
  private readonly apiUrl = `${environment.apiUrl}/category_rules`;
  private rulesSubject = new BehaviorSubject<CategoryRule[]>([]);
  public rules$ = this.rulesSubject.asObservable();

  constructor(private http: HttpClient) {}

  /**
   * Get all categorization rules.
   */
  getAllRules(): Observable<CategoryRule[]> {
    return this.http.get<{ response: CategoryRule[]; details: string }>(this.apiUrl).pipe(
      tap((payload) => {
        const rules = payload?.response || [];
        this.rulesSubject.next(rules);
      }),
      map((payload) => payload?.response || [])
    );
  }

  /**
   * Get a specific rule by ID.
   */
  getRuleById(id: number): Observable<CategoryRule> {
    return this.http
      .get<{ response: CategoryRule; details: string }>(`${this.apiUrl}/${id}`)
      .pipe(map((payload) => payload?.response));
  }

  /**
   * Create a new categorization rule.
   */
  createRule(rule: CategoryRule): Observable<CategoryRule> {
    return this.http
      .post<{ response: CategoryRule; details: string }>(this.apiUrl, rule)
      .pipe(
        map((payload) => payload?.response),
        tap((newRule) => {
          if (newRule) {
            const current = this.rulesSubject.value;
            this.rulesSubject.next([...current, newRule]);
          }
        })
      );
  }

  /**
   * Update an existing rule.
   */
  updateRule(id: number, updates: CategoryRuleUpdate): Observable<CategoryRule> {
    return this.http
      .patch<{ response: CategoryRule; details: string }>(`${this.apiUrl}/${id}`, updates)
      .pipe(
        map((payload) => payload?.response),
        tap((updated) => {
          if (updated) {
            const current = this.rulesSubject.value;
            const index = current.findIndex((r) => r.id === id);
            if (index !== -1) {
              current[index] = updated;
              this.rulesSubject.next([...current]);
            }
          }
        })
      );
  }

  /**
   * Delete a rule.
   */
  deleteRule(id: number): Observable<void> {
    return this.http.delete<{ response: unknown; details: string }>(`${this.apiUrl}/${id}`).pipe(
      tap(() => {
        const current = this.rulesSubject.value;
        this.rulesSubject.next(current.filter((r) => r.id !== id));
      }),
      map(() => undefined as void)
    );
  }

  /**
   * Refresh the rules cache from the server.
   */
  refreshRules(): Observable<CategoryRule[]> {
    return this.getAllRules();
  }
}
