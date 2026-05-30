import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { forkJoin } from 'rxjs';
import { MatDialog } from '@angular/material/dialog';
import { GenericTableComponent, TableColumn } from '@shared/generic-table/generic-table.component';
import { GenericDialogComponent } from '@shared/generic-dialog/generic-dialog.component';
import { ToastService } from '@core_services/toast.service';
import { environment } from '@env/environment';
import { ApiResponse } from '@app/models/core/APIResponse';
import { IncomeBase as Income } from '@incomes_models/IncomeBase';
import { IncomeCategoryBase as IncomeCategory } from '@incomes_models/IncomeCategoryBase';
import { SourceBase as Source } from '@finance_models/SourceBase';
import { AccountBase as Account } from '@finance_models/AccountBase';
import { FormFieldConfig } from '@shared/generic-form/form-config';
import { IncomeService } from '@incomes_services/income.service';
import { FormFactoryService } from '@app/core/factories/form-factory.service';
import { UtilsService } from '@app/utils/utils.service';
import { IncomeCategoryService } from '@incomes_services/income-category.service';
import { AccountService } from '@finance_services/account.service';
import { SourceService } from '@finance_services/source.service';
import { MetaService } from '@core_services/meta.service';

@Component({
  selector: 'app-incomes-component',
  imports: [GenericTableComponent],
  templateUrl: './incomes-component.html',
  styleUrl: './incomes-component.css',
})
export class IncomesComponent implements OnInit {
  incomes: Income[] = [];
  filterValue = '';
  isLoading = false;
  errorMessage = '';
  formFields: FormFieldConfig[] = [];
  columns: TableColumn<Income>[] = [];
  categoryMap: Record<number, string> = {};
  accountsMap: Record<number, string> = {};
  sourcesMap: Record<number, string> = {};

  constructor(
    private incomeService: IncomeService,
    private incomecategoryService: IncomeCategoryService,
    private utilsService: UtilsService,
    private cdr: ChangeDetectorRef,
    private dialog: MatDialog,
    private toastService: ToastService,
    private formFactory: FormFactoryService,
    private metaService: MetaService,
    private accountService: AccountService,
    private sourceService: SourceService
  ) {}

  ngOnInit(): void {
    this.loadInitialData();
  }

  private loadInitialData(): void {
    this.isLoading = true;
    forkJoin({
      incomes: this.incomeService.getAll(),
      meta: this.metaService.getMeta('income'),
      categories: this.incomecategoryService.getAll(),
      sources: this.sourceService.getAll(),
      accounts: this.accountService.getAll(),
    }).subscribe({
      next: ({ incomes, meta, categories, sources, accounts }) => {
        this.incomes = incomes.response || [];

        this.categoryMap = Object.fromEntries(
          categories.response.map((c: IncomeCategory) => [c.id as number, c.name])
        );
        this.sourcesMap = Object.fromEntries(
          sources.response.map((s: Source) => [s.id as number, s.name])
        );
        this.accountsMap = Object.fromEntries(
          accounts.response.map((a: Account) => [a.id as number, a.name])
        );

        const relationOptions = {
          'income-category': categories.response.map((c: IncomeCategory) => ({ value: c.id as number, label: c.name })),
          source: sources.response.map((s: Source) => ({ value: s.id as number, label: s.name })),
          account: accounts.response.map((a: Account) => ({ value: a.id as number, label: a.name })),
        };

        this.formFields = this.formFactory.enrichMetadataFields(meta.fields, relationOptions);
        const baseCols = this.formFactory.getTableColumnsFromMetadata<Income>(this.formFields);
        this.columns = baseCols.map((col) => {
          if (col.key === 'category_id') return { ...col, formatter: (v: number) => this.categoryMap[v] ?? String(v) };
          if (col.key === 'source_id') return { ...col, formatter: (v: number) => this.sourcesMap[v] ?? String(v) };
          if (col.key === 'account_id') return { ...col, formatter: (v: number) => this.accountsMap[v] ?? String(v) };
          if (col.key === 'date') return { ...col, formatter: (v: string) => this.utilsService.formatDateShortStr(v) };
          return col;
        });

        this.isLoading = false;
        this.cdr.detectChanges();
      },
      error: () => {
        this.errorMessage = 'Error loading income data.';
        this.isLoading = false;
      },
    });
  }

  openDialog(data?: Income): void {
    const dialogRef = this.dialog.open(GenericDialogComponent, {
      data: {
        title: data ? 'Edit Income' : 'New Income',
        fields: this.formFields,
        initialData: data || {},
      },
    });

    dialogRef.afterClosed().subscribe((result) => {
      if (result) {
        result.id ? this.update(result) : this.create(result);
      }
    });
  }

  edit(income: Income): void {
    this.openDialog(income);
  }

  add(): void {
    this.openDialog();
  }

  update(income: Income): void {
    this.incomeService.update(income.id!, income).subscribe({
      next: (response: ApiResponse<Income>) => {
        const updated = response.response;
        const index = this.incomes.findIndex((h) => h.id === updated.id);
        if (index !== -1) {
          this.incomes[index] = updated;
          this.incomes = [...this.incomes];
        }
        this.toastService.showToast(response, environment.toastType.Success, {});
        this.cdr.detectChanges();
      },
      error: (err) => {
        this.toastService.showToast(err.error as ApiResponse<string>, environment.toastType.Error, {});
      },
    });
  }

  create(income: Income): void {
    this.incomeService.create(income).subscribe({
      next: (response: ApiResponse<Income>) => {
        this.incomes.push(response.response);
        this.incomes = [...this.incomes];
        this.toastService.showToast(response, environment.toastType.Success, {});
        this.cdr.detectChanges();
      },
      error: (err) => {
        this.toastService.showToast(err.error as ApiResponse<string>, environment.toastType.Error, {});
      },
    });
  }

  applyFilter(event: Event) {
    this.filterValue = (event.target as HTMLInputElement).value.trim().toLowerCase();
  }
}
