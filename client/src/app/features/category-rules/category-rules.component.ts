/**
 * Category Rule Management Component
 */

import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatDialog } from '@angular/material/dialog';
import { Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';
import { MATERIAL_IMPORTS } from '@utils/material.imports';
import { FormFieldConfig } from '@shared/generic-form/form-config';
import { GenericDialogComponent } from '@shared/generic-dialog/generic-dialog.component';

import { CategoryRuleService, CategoryRule } from '@services/category-rule/category-rule.service';
import { ExpenseCategoryService } from '@services/expenses/expense-category.service';
import { IncomeCategoryService } from '@services/incomes/income-category.service';
import { InvestmentCategoryService } from '@services/investments/investment-category.service';
import { GenericTableComponent, TableColumn } from '@shared/generic-table/generic-table.component';
import { regexValidator } from '@utils/validators/regex.validator';

@Component({
  selector: 'app-category-rules',
  standalone: true,
  imports: [CommonModule, ...MATERIAL_IMPORTS, GenericTableComponent],
  templateUrl: './category-rules.component.html',
  styleUrls: ['./category-rules.component.scss'],
})
export class CategoryRulesComponent implements OnInit, OnDestroy {
  rules: CategoryRule[] = [];
  loading = false;
  error: string | null = null;
  filterType: 'expense' | 'income' | 'investment' | 'all' = 'all';

  expenseCategories: { id: number; name: string }[] = [];
  incomeCategories: { id: number; name: string }[] = [];
  investmentCategories: { id: number; name: string }[] = [];

  columns: TableColumn<CategoryRule>[] = [
    { key: 'name', label: 'Name', sortable: true },
    { key: 'type', label: 'Type', sortable: true },
    { key: 'pattern', label: 'Pattern', sortable: false },
    {
      key: 'category_id',
      label: 'Category',
      sortable: true,
      formatter: (value: number, row: CategoryRule) => this.getCategoryLabel(row.type, value),
    },
    { key: 'priority', label: 'Priority', sortable: true },
    {
      key: 'is_active',
      label: 'Active',
      sortable: true,
      formatter: (value: boolean) => (value ? 'Yes' : 'No'),
    },
  ];
  dialogFields: FormFieldConfig[] = [
    { key: 'id', label: 'Id', type: 'number' },
    {
      key: 'name',
      label: 'Rule Name',
      type: 'text',
      required: true,
      minLength: 3,
    },
    {
      key: 'type',
      label: 'Transaction Type',
      type: 'select',
      required: true,
      options: [
        { value: 'expense', label: 'Expense' },
        { value: 'income', label: 'Income' },
        { value: 'investment', label: 'Investment' },
      ],
    },
    {
      key: 'pattern',
      label: 'Regex Pattern',
      type: 'text',
      required: true,
      validators: [regexValidator()],
    },
    {
      key: 'category_id',
      label: 'Category ID',
      type: 'number',
      required: true,
      min: 1,
    },
    {
      key: 'priority',
      label: 'Priority',
      type: 'number',
      required: true,
      min: 0,
    },
    { key: 'is_active', label: 'Rule is Active', type: 'checkbox' },
  ];

  private destroy$ = new Subject<void>();

  constructor(
    private categoryRuleService: CategoryRuleService,
    private expenseCategoryService: ExpenseCategoryService,
    private incomeCategoryService: IncomeCategoryService,
    private investmentCategoryService: InvestmentCategoryService,
    private dialog: MatDialog,
  ) {}

  ngOnInit(): void {
    this.loadRules();
    this.loadCategoryLists();
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

  private loadCategoryLists(): void {
    this.expenseCategoryService.getAll().pipe(takeUntil(this.destroy$)).subscribe({
      next: (resp) => this.expenseCategories = (resp?.response || [])
        .filter((c) => c.id !== undefined && c.id !== null)
        .map((c) => ({ id: c.id as number, name: c.name })),
      error: err => console.error('Error loading expense categories:', err)
    });

    this.incomeCategoryService.getAll().pipe(takeUntil(this.destroy$)).subscribe({
      next: (resp) => this.incomeCategories = (resp?.response || [])
        .filter((c) => c.id !== undefined && c.id !== null)
        .map((c) => ({ id: c.id as number, name: c.name })),
      error: err => console.error('Error loading income categories:', err)
    });

    this.investmentCategoryService.getAll().pipe(takeUntil(this.destroy$)).subscribe({
      next: (resp) => this.investmentCategories = (resp?.response || [])
        .filter((c) => c.id !== undefined && c.id !== null)
        .map((c) => ({ id: c.id as number, name: c.name })),
      error: err => console.error('Error loading investment categories:', err)
    });
  }

  private getCategoryLabel(type: 'expense' | 'income' | 'investment', categoryId?: number): string {
    if (!categoryId) {
      return '-';
    }

    const list = type === 'expense' ? this.expenseCategories :
                 type === 'income' ? this.incomeCategories :
                 this.investmentCategories;

    const category = list.find(c => c.id === categoryId);
    return category ? category.name : `#${categoryId}`;
  }

  private getCategoryOptions(type: 'expense' | 'income' | 'investment') {
    const list = type === 'expense' ? this.expenseCategories :
                 type === 'income' ? this.incomeCategories :
                 this.investmentCategories;
    return list.map(c => ({ value: c.id, label: c.name }));
  }

  private getCategoryLabelByType(type: 'expense' | 'income' | 'investment'): string {
    if (type === 'expense') return 'Category Expense';
    if (type === 'income') return 'Category Income';
    return 'Category Investment';
  }

  private getDialogFields(type: 'expense' | 'income' | 'investment'): FormFieldConfig[] {
    const fields: FormFieldConfig[] = [
      { key: 'id', label: 'Id', type: 'number' },
      {
        key: 'name',
        label: 'Rule Name',
        type: 'text',
        required: true,
        minLength: 3,
      },
      {
        key: 'type',
        label: 'Transaction Type',
        type: 'select',
        required: true,
        options: [
          { value: 'expense', label: 'Expense' },
          { value: 'income', label: 'Income' },
          { value: 'investment', label: 'Investment' },
        ],
        onChange: (newType: 'expense' | 'income' | 'investment', form) => {
          const categoryField = fields.find((f) => f.key === 'category_id');
          if (!categoryField) return;

          categoryField.label = this.getCategoryLabelByType(newType);
          categoryField.options = this.getCategoryOptions(newType);

          if (form?.get('category_id')) {
            form.get('category_id')!.setValue(null);
          }
        },
      },
      {
        key: 'pattern',
        label: 'Regex Pattern',
        type: 'text',
        required: true,
        validators: [regexValidator()],
      },
      {
        key: 'category_id',
        label: this.getCategoryLabelByType(type),
        type: 'select',
        required: true,
        options: this.getCategoryOptions(type),
      },
      {
        key: 'priority',
        label: 'Priority',
        type: 'number',
        required: true,
        min: 0,
      },
      { key: 'is_active', label: 'Rule is Active', type: 'checkbox' },
    ];

    return fields;
  }

  private isCategoryIdValidForType(type: 'expense' | 'income' | 'investment', categoryId: number): boolean {
    if (!categoryId) return false;
    return this.getCategoryOptions(type).some((option) => option.value === categoryId);
  }


  openCreateDialog(): void {
    const fields = this.getDialogFields('expense');

    const dialogRef = this.dialog.open(GenericDialogComponent, {
      width: '600px',
      data: {
        title: 'Create New Rule',
        fields,
        initialData: {
          type: 'expense',
          category_id: this.expenseCategories?.[0]?.id || null,
          priority: 100,
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

  openEditDialog(rule: CategoryRule): void {
    const fields = this.getDialogFields(rule.type);

    const dialogRef = this.dialog.open(GenericDialogComponent, {
      width: '600px',
      data: {
        title: 'Edit Rule',
        fields,
        initialData: rule,
      },
    });

    dialogRef
      .afterClosed()
      .pipe(takeUntil(this.destroy$))
      .subscribe((result) => {
        if (result && rule.id) {
          if (!this.isCategoryIdValidForType(result.type || rule.type, result.category_id || rule.category_id)) {
            this.error = `Invalid category_id ${result.category_id || rule.category_id} for type ${result.type || rule.type}`;
            return;
          }
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
    if (!this.isCategoryIdValidForType(rule.type, rule.category_id)) {
      this.error = `Invalid category_id ${rule.category_id} for type ${rule.type}`;
      return;
    }

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
