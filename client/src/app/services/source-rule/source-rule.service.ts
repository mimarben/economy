/**
 * Service for managing Source Rules via HTTP API.
 *
 * Provides CRUD operations for source rule associations used in transaction categorization.
 */

import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, BehaviorSubject } from 'rxjs';
import { tap, map } from 'rxjs/operators';
import { BaseCrudService } from '@core_services/base-crud.service';

export interface SourceRule {
  id?: number;
  category_rule_id: number;
  source_id: number;
  is_active: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface SourceRuleUpdate {
  category_rule_id?: number;
  source_id?: number;
  is_active?: boolean;
}

@Injectable({
  providedIn: 'root',
})
export class SourceRuleService extends BaseCrudService<SourceRule> {
  private rulesSubject = new BehaviorSubject<SourceRule[]>([]);
  public rules$ = this.rulesSubject.asObservable();

  /**
   * Get all source rules.
   */
  getAllRules(): Observable<SourceRule[]> {
    return this.getAll().pipe(
      tap((payload) => {
        const rules = (payload?.response || []) as SourceRule[];
        this.rulesSubject.next(rules);
      }),
      map((payload) => payload?.response || []),
    );
  }

  /**
   * Get a specific rule by ID.
   */
  getRuleById(id: number): Observable<SourceRule> {
    return this.getById(id).pipe(
      map((payload) => payload?.response as SourceRule),
    );
  }

  /**
   * Get all active rules for a category rule.
   */
  getActiveByCategoryRule(categoryRuleId: number): Observable<SourceRule[]> {
    return this.http.get<any>(`/source_rules/by_category_rule/${categoryRuleId}`).pipe(
      map((payload) => payload?.response || []),
    );
  }

  /**
   * Create a new source rule.
   */
  createRule(rule: SourceRule): Observable<SourceRule> {
    return this.create(rule).pipe(
      map((payload) => payload?.response as SourceRule),
      tap((newRule) => {
        if (newRule) {
          const current = this.rulesSubject.value;
          this.rulesSubject.next([...current, newRule]);
        }
      }),
    );
  }

  /**
   * Update an existing rule.
   */
  updateRule(
    id: number,
    updates: SourceRuleUpdate,
  ): Observable<SourceRule> {
    return this.update(id, updates as any).pipe(
      map((payload) => payload?.response as SourceRule),
      tap((updated) => {
        if (updated) {
          const current = this.rulesSubject.value;
          const index = current.findIndex((r) => r.id === id);
          if (index !== -1) {
            current[index] = updated;
            this.rulesSubject.next([...current]);
          }
        }
      }),
    );
  }

  /**
   * Delete a rule.
   */
  deleteRule(id: number): Observable<void> {
    return this.delete(id).pipe(
      tap(() => {
        const current = this.rulesSubject.value;
        this.rulesSubject.next(current.filter((r) => r.id !== id));
      }),
      map(() => undefined as void),
    );
  }

  /**
   * Refresh the rules cache from the server.
   */
  refreshRules(): Observable<SourceRule[]> {
    return this.getAllRules();
  }

  constructor(protected override http: HttpClient) {
    super(http, 'source_rules');
  }
}
