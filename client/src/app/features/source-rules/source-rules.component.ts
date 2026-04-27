/**
 * Source Rule Management Component
 */

import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatDialog } from '@angular/material/dialog';
import { Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';
import { MATERIAL_IMPORTS } from '@utils/material.imports';
import { FormFieldConfig } from '@shared/generic-form/form-config';
import { GenericDialogComponent } from '@shared/generic-dialog/generic-dialog.component';

import { SourceRuleService, SourceRule } from '@services/source-rule/source-rule.service';
import { CategoryRuleService, CategoryRule } from '@services/category-rule/category-rule.service';
import { SourceService } from '@services/finance/source.service';
import { GenericTableComponent, TableColumn } from '@shared/generic-table/generic-table.component';

@Component({
  selector: 'app-source-rules',
  standalone: true,
  imports: [CommonModule, ...MATERIAL_IMPORTS, GenericTableComponent],
  templateUrl: './source-rules.component.html',
  styleUrls: ['./source-rules.component.scss'],
})
export class SourceRulesComponent implements OnInit, OnDestroy {
  rules: SourceRule[] = [];
  loading = false;
  error: string | null = null;

  categoryRules: CategoryRule[] = [];
  sources: { id: number; name: string }[] = [];

  columns: TableColumn<SourceRule>[] = [
    {
      key: 'category_rule_id',
      label: 'Category Rule',
      sortable: true,
      formatter: (value: number) => this.getCategoryRuleLabel(value),
    },
    {
      key: 'source_id',
      label: 'Source',
      sortable: true,
      formatter: (value: number) => this.getSourceLabel(value),
    },
    {
      key: 'is_active',
      label: 'Active',
      sortable: true,
      formatter: (value: boolean) => (value ? 'Yes' : 'No'),
    },
  ];

  private destroy$ = new Subject<void>();

  constructor(
    private sourceRuleService: SourceRuleService,
    private categoryRuleService: CategoryRuleService,
    private sourceService: SourceService,
    private dialog: MatDialog,
  ) {}

  ngOnInit(): void {
    this.loadRules();
    this.loadCategoryRules();
    this.loadSources();
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  loadRules(): void {
    this.loading = true;
    this.error = null;

    this.sourceRuleService
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

  private loadCategoryRules(): void {
    this.categoryRuleService.getAllRules().pipe(takeUntil(this.destroy$)).subscribe({
      next: (rules) => (this.categoryRules = rules),
      error: (err) => console.error('Error loading category rules:', err),
    });
  }

  private loadSources(): void {
    this.sourceService.getAll().pipe(takeUntil(this.destroy$)).subscribe({
      next: (resp) =>
        (this.sources = (resp?.response || [])
          .filter((s) => s.id !== undefined && s.id !== null)
          .map((s) => ({ id: s.id as number, name: s.name }))),
      error: (err) => console.error('Error loading sources:', err),
    });
  }

  private getCategoryRuleLabel(categoryRuleId?: number): string {
    if (!categoryRuleId) {
      return '-';
    }

    const rule = this.categoryRules.find((c) => c.id === categoryRuleId);
    return rule ? rule.name : `#${categoryRuleId}`;
  }

  private getSourceLabel(sourceId?: number): string {
    if (!sourceId) {
      return '-';
    }

    const source = this.sources.find((s) => s.id === sourceId);
    return source ? source.name : `#${sourceId}`;
  }

  private getCategoryRuleOptions() {
    return this.categoryRules.map((c) => ({ value: c.id, label: c.name }));
  }

  private getSourceOptions() {
    return this.sources.map((s) => ({ value: s.id, label: s.name }));
  }

  private getDialogFields(): FormFieldConfig[] {
    return [
      { key: 'id', label: 'Id', type: 'number' },
      {
        key: 'category_rule_id',
        label: 'Category Rule',
        type: 'select',
        required: true,
        options: this.getCategoryRuleOptions(),
      },
      {
        key: 'source_id',
        label: 'Source',
        type: 'select',
        required: true,
        options: this.getSourceOptions(),
      },
      { key: 'is_active', label: 'Rule is Active', type: 'checkbox' },
    ];
  }

  private isCategoryRuleIdValid(categoryRuleId: number): boolean {
    if (!categoryRuleId) return false;
    return this.getCategoryRuleOptions().some((option) => option.value === categoryRuleId);
  }

  private isSourceIdValid(sourceId: number): boolean {
    if (!sourceId) return false;
    return this.getSourceOptions().some((option) => option.value === sourceId);
  }

  openCreateDialog(): void {
    const fields = this.getDialogFields();

    const dialogRef = this.dialog.open(GenericDialogComponent, {
      width: '600px',
      data: {
        title: 'Create New Source Rule',
        fields,
        initialData: {
          category_rule_id: this.categoryRules?.[0]?.id || null,
          source_id: this.sources?.[0]?.id || null,
          is_active: true,
        },
      },
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

  openEditDialog(rule: SourceRule): void {
    const fields = this.getDialogFields();

    const dialogRef = this.dialog.open(GenericDialogComponent, {
      width: '600px',
      data: {
        title: 'Edit Source Rule',
        fields,
        initialData: rule,
      },
    });

    dialogRef
      .afterClosed()
      .pipe(takeUntil(this.destroy$))
      .subscribe((result) => {
        if (result && rule.id) {
          if (!this.isCategoryRuleIdValid(result.category_rule_id || rule.category_rule_id)) {
            this.error = `Invalid category_rule_id ${result.category_rule_id || rule.category_rule_id}`;
            return;
          }
          if (!this.isSourceIdValid(result.source_id || rule.source_id)) {
            this.error = `Invalid source_id ${result.source_id || rule.source_id}`;
            return;
          }
          this.updateRule(rule.id, result);
        }
      });
  }

  onDeleteRule(rule: SourceRule): void {
    if (!rule.id) {
      return;
    }
    this.deleteRule(rule.id);
  }

  private createRule(rule: SourceRule): void {
    if (!this.isCategoryRuleIdValid(rule.category_rule_id)) {
      this.error = `Invalid category_rule_id ${rule.category_rule_id}`;
      return;
    }
    if (!this.isSourceIdValid(rule.source_id)) {
      this.error = `Invalid source_id ${rule.source_id}`;
      return;
    }

    this.loading = true;
    this.sourceRuleService
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

  private updateRule(id: number, updates: Partial<SourceRule>): void {
    this.loading = true;
    this.sourceRuleService
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

  private deleteRule(id: number): void {
    if (!confirm('Are you sure you want to delete this source rule?')) {
      return;
    }

    this.loading = true;
    this.sourceRuleService
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
