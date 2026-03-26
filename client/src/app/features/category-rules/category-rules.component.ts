/**
 * Category Rule Management Component
 * 
 * Provides CRUD interface for managing transaction categorization rules.
 * Features:
 * - Table view with sorting/filtering
 * - Create, Edit, Delete forms
 * - Regex pattern validation
 * - Real-time updates via BehaviorSubject
 */

import { Component, OnInit, OnDestroy, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MatTableDataSource } from '@angular/material/table';
import { MatDialog } from '@angular/material/dialog';
import { Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';
import { MaterialModule } from '@app/utils/material.module';

import { CategoryRuleService, CategoryRule } from '../../services/category-rule/category-rule.service';
import { CategoryRuleFormComponent } from './category-rule-form/category-rule-form.component';

@Component({
  selector: 'app-category-rules',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MaterialModule,
  ],
  templateUrl: './category-rules.component.html',
  styleUrls: ['./category-rules.component.scss'],
})
export class CategoryRulesComponent implements OnInit, OnDestroy {
  displayedColumns: string[] = [
    'name',
    'type',
    'pattern',
    'priority',
    'is_active',
    'actions'
  ];
  dataSource = new MatTableDataSource<CategoryRule>([]);
  loading = false;
  error: string | null = null;
  filterType: 'expense' | 'income' | 'investment' | 'all' = 'all';

  private destroy$ = new Subject<void>();

  constructor(
    private categoryRuleService: CategoryRuleService,
    private dialog: MatDialog
  ) {}

  ngOnInit(): void {
    this.loadRules();
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  /**
   * Load all rules from the backend.
   */
  loadRules(): void {
    this.loading = true;
    this.error = null;
    
    this.categoryRuleService.getAllRules()
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (rules) => {
          this.dataSource.data = rules;
          this.loading = false;
        },
        error: (error) => {
          this.error = 'Failed to load rules. Please try again.';
          console.error('Error loading rules:', error);
          this.loading = false;
        }
      });
  }

  /**
   * Filter rules by transaction type.
   */
  filterByType(type: 'expense' | 'income' | 'investment' | 'all'): void {
    this.filterType = type;
    if (type === 'all') {
      // Reload all rules
      this.loadRules();
    } else {
      // Load only active rules for this type
      this.loading = true;
      this.categoryRuleService.getActiveRulesByType(type)
        .pipe(takeUntil(this.destroy$))
        .subscribe({
          next: (rules) => {
            this.dataSource.data = rules;
            this.loading = false;
          },
          error: (error) => {
            this.error = `Failed to load ${type} rules.`;
            this.loading = false;
          }
        });
    }
  }

  /**
   * Open dialog to create a new rule.
   */
  openCreateDialog(): void {
    const dialogRef = this.dialog.open(CategoryRuleFormComponent, {
      width: '600px',
      data: { mode: 'create' }
    });

    dialogRef.afterClosed()
      .pipe(takeUntil(this.destroy$))
      .subscribe((result) => {
        if (result) {
          this.createRule(result);
        }
      });
  }

  /**
   * Open dialog to edit an existing rule.
   */
  openEditDialog(rule: CategoryRule): void {
    const dialogRef = this.dialog.open(CategoryRuleFormComponent, {
      width: '600px',
      data: { mode: 'edit', rule }
    });

    dialogRef.afterClosed()
      .pipe(takeUntil(this.destroy$))
      .subscribe((result) => {
        if (result && rule.id) {
          this.updateRule(rule.id, result);
        }
      });
  }

  /**
   * Create a new rule.
   */
  private createRule(rule: CategoryRule): void {
    this.loading = true;
    this.categoryRuleService.createRule(rule)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: () => {
          this.loadRules();
        },
        error: (error) => {
          this.error = 'Failed to create rule.';
          console.error('Error creating rule:', error);
          this.loading = false;
        }
      });
  }

  /**
   * Update an existing rule.
   */
  private updateRule(id: number, updates: Partial<CategoryRule>): void {
    this.loading = true;
    this.categoryRuleService.updateRule(id, updates)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: () => {
          this.loadRules();
        },
        error: (error) => {
          this.error = 'Failed to update rule.';
          console.error('Error updating rule:', error);
          this.loading = false;
        }
      });
  }

  /**
   * Delete a rule with confirmation.
   */
  deleteRule(id: number, name: string): void {
    if (confirm(`Are you sure you want to delete the rule "${name}"?`)) {
      this.loading = true;
      this.categoryRuleService.deleteRule(id)
        .pipe(takeUntil(this.destroy$))
        .subscribe({
          next: () => {
            this.loadRules();
          },
          error: (error) => {
            this.error = 'Failed to delete rule.';
            console.error('Error deleting rule:', error);
            this.loading = false;
          }
        });
    }
  }

  /**
   * Apply filter to the table.
   */
  applyFilter(event: Event): void {
    const filterValue = (event.target as HTMLInputElement).value;
    this.dataSource.filter = filterValue.trim().toLowerCase();
  }
}
