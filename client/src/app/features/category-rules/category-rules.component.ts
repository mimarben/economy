/**
 * Category Rule Management Component
 */

import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatDialog } from '@angular/material/dialog';
import { Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';
import { MaterialModule } from '@app/utils/material.module';

import { CategoryRuleService, CategoryRule } from '../../services/category-rule/category-rule.service';
import { CategoryRuleFormComponent } from './category-rule-form/category-rule-form.component';
import { GenericTableComponent, TableColumn } from '../../shared/components/generic-table/generic-table.component';

@Component({
  selector: 'app-category-rules',
  standalone: true,
  imports: [CommonModule, MaterialModule, GenericTableComponent],
  templateUrl: './category-rules.component.html',
  styleUrls: ['./category-rules.component.scss'],
})
export class CategoryRulesComponent implements OnInit, OnDestroy {
  rules: CategoryRule[] = [];
  loading = false;
  error: string | null = null;
  filterType: 'expense' | 'income' | 'investment' | 'all' = 'all';

  columns: TableColumn<CategoryRule>[] = [
    { key: 'name', label: 'Name', sortable: true },
    { key: 'type', label: 'Type', sortable: true },
    { key: 'pattern', label: 'Pattern', sortable: false },
    { key: 'priority', label: 'Priority', sortable: true },
    {
      key: 'is_active',
      label: 'Active',
      sortable: true,
      formatter: (value: boolean) => (value ? 'Yes' : 'No'),
    },
  ];

  private destroy$ = new Subject<void>();

  constructor(
    private categoryRuleService: CategoryRuleService,
    private dialog: MatDialog,
  ) {}

  ngOnInit(): void {
    this.loadRules();
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  loadRules(): void {
    this.loading = true;
    this.error = null;

    this.categoryRuleService
      .getAllRules()
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (rules) => {
          this.rules = rules;
          this.loading = false;
        },
        error: (error) => {
          this.error = 'Failed to load rules. Please try again.';
          console.error('Error loading rules:', error);
          this.loading = false;
        },
      });
  }

  filterByType(type: 'expense' | 'income' | 'investment' | 'all'): void {
    this.filterType = type;
    if (type === 'all') {
      this.loadRules();
      return;
    }

    this.loading = true;
    this.categoryRuleService
      .getActiveRulesByType(type)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (rules) => {
          this.rules = rules;
          this.loading = false;
        },
        error: () => {
          this.error = `Failed to load ${type} rules.`;
          this.loading = false;
        },
      });
  }

  openCreateDialog(): void {
    const dialogRef = this.dialog.open(CategoryRuleFormComponent, {
      width: '600px',
      data: { mode: 'create' },
    });

    dialogRef
      .afterClosed()
      .pipe(takeUntil(this.destroy$))
      .subscribe((result) => {
        if (result) {
          this.createRule(result);
        }
      });
  }

  openEditDialog(rule: CategoryRule): void {
    const dialogRef = this.dialog.open(CategoryRuleFormComponent, {
      width: '600px',
      data: { mode: 'edit', rule },
    });

    dialogRef
      .afterClosed()
      .pipe(takeUntil(this.destroy$))
      .subscribe((result) => {
        if (result && rule.id) {
          this.updateRule(rule.id, result);
        }
      });
  }

  onDeleteRule(rule: CategoryRule): void {
    if (!rule.id) {
      return;
    }
    this.deleteRule(rule.id, rule.name);
  }

  private createRule(rule: CategoryRule): void {
    this.loading = true;
    this.categoryRuleService
      .createRule(rule)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: () => this.loadRules(),
        error: (error) => {
          this.error = 'Failed to create rule.';
          console.error('Error creating rule:', error);
          this.loading = false;
        },
      });
  }

  private updateRule(id: number, updates: Partial<CategoryRule>): void {
    this.loading = true;
    this.categoryRuleService
      .updateRule(id, updates)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: () => this.loadRules(),
        error: (error) => {
          this.error = 'Failed to update rule.';
          console.error('Error updating rule:', error);
          this.loading = false;
        },
      });
  }

  private deleteRule(id: number, name: string): void {
    if (!confirm(`Are you sure you want to delete the rule "${name}"?`)) {
      return;
    }

    this.loading = true;
    this.categoryRuleService
      .deleteRule(id)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: () => this.loadRules(),
        error: (error) => {
          this.error = 'Failed to delete rule.';
          console.error('Error deleting rule:', error);
          this.loading = false;
        },
      });
  }
}
