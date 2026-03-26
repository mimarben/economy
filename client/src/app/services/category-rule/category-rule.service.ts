/**
 * Service for managing Category Rules via HTTP API.
 * 
 * Provides CRUD operations for categorization rules used in transaction import workflow.
 */

import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, BehaviorSubject } from 'rxjs';
import { tap } from 'rxjs/operators';
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
    return this.http.get<CategoryRule[]>(this.apiUrl).pipe(
      tap(rules => this.rulesSubject.next(rules))
    );
  }

  /**
   * Get active rules for a specific transaction type.
   * Rules are ordered by priority (DESC).
   */
  getActiveRulesByType(type: 'expense' | 'income' | 'investment'): Observable<CategoryRule[]> {
    return this.http.get<CategoryRule[]>(`${this.apiUrl}/by_type/${type}`);
  }

  /**
   * Get a specific rule by ID.
   */
  getRuleById(id: number): Observable<CategoryRule> {
    return this.http.get<CategoryRule>(`${this.apiUrl}/${id}`);
  }

  /**
   * Create a new categorization rule.
   */
  createRule(rule: CategoryRule): Observable<CategoryRule> {
    return this.http.post<CategoryRule>(this.apiUrl, rule).pipe(
      tap(newRule => {
        const current = this.rulesSubject.value;
        this.rulesSubject.next([...current, newRule]);
      })
    );
  }

  /**
   * Update an existing rule.
   */
  updateRule(id: number, updates: CategoryRuleUpdate): Observable<CategoryRule> {
    return this.http.patch<CategoryRule>(`${this.apiUrl}/${id}`, updates).pipe(
      tap(updated => {
        const current = this.rulesSubject.value;
        const index = current.findIndex(r => r.id === id);
        if (index !== -1) {
          current[index] = updated;
          this.rulesSubject.next([...current]);
        }
      })
    );
  }

  /**
   * Delete a rule.
   */
  deleteRule(id: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/${id}`).pipe(
      tap(() => {
        const current = this.rulesSubject.value;
        this.rulesSubject.next(current.filter(r => r.id !== id));
      })
    );
  }

  /**
   * Refresh the rules cache from the server.
   */
  refreshRules(): Observable<CategoryRule[]> {
    return this.getAllRules();
  }
}
