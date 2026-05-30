import { Component, ChangeDetectorRef, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { forkJoin } from 'rxjs';
import { GenericDialogComponent } from '@shared/generic-dialog/generic-dialog.component';
import { GenericTableComponent, TableColumn } from '@shared/generic-table/generic-table.component';
import { ApiResponse } from '@app/models/core/APIResponse';
import { FormFactoryService } from '@app/core/factories/form-factory.service';
import { FormFieldConfig } from '@shared/generic-form/form-config';
import { ToastService } from '@core_services/toast.service';
import { environment } from '@env/environment';
import { InvestmentBase as Investment } from '@investments_models/InvestmentBase';
import { InvestmentService } from '@investments_services/investment.service';
import { AccountService } from '@finance_services/account.service';
import { InvestmentCategoryService } from '@investments_services/investment-category.service';
import { AccountBase as Account } from '@finance_models/AccountBase';
import { InvestmentCategoryBase as InvestmentCategory } from '@investments_models/InvestmentCategoryBase';
import { MetaService } from '@core_services/meta.service';
import { UtilsService } from '@app/utils/utils.service';

@Component({
  selector: 'app-investments',
  imports: [GenericTableComponent],
  templateUrl: './investments.component.html',
  styleUrl: './investments.component.css'
})
export class InvestmentsComponent implements OnInit {
  investments: Investment[] = [];
  filterValue = '';
  errorMessage = '';
  isLoading = false;
  formFields: FormFieldConfig[] = [];
  columns: TableColumn<Investment>[] = [];
  accountMap: Record<number, string> = {};
  categoryMap: Record<number, string> = {};

  constructor(
    private investmentService: InvestmentService,
    private accountService: AccountService,
    private investmentCategoryService: InvestmentCategoryService,
    private metaService: MetaService,
    private utilsService: UtilsService,
    private cdr: ChangeDetectorRef,
    private dialog: MatDialog,
    private toastService: ToastService,
    private formFactory: FormFactoryService,
  ) {}

  ngOnInit(): void {
    this.loadInitialData();
  }

  private loadInitialData(): void {
    this.isLoading = true;
    forkJoin({
      investments: this.investmentService.getAll(),
      meta: this.metaService.getMeta('investment'),
      accounts: this.accountService.getAll(),
      categories: this.investmentCategoryService.getAll(),
    }).subscribe({
      next: ({ investments, meta, accounts, categories }) => {
        this.investments = investments.response;

        this.accountMap = Object.fromEntries(
          accounts.response.map((a: Account) => [a.id as number, a.name])
        );
        this.categoryMap = Object.fromEntries(
          categories.response.map((c: InvestmentCategory) => [c.id as number, c.name])
        );

        const relationOptions = {
          account: accounts.response.map((a: Account) => ({ value: a.id as number, label: a.name })),
          'investment-category': categories.response.map((c: InvestmentCategory) => ({ value: c.id as number, label: c.name })),
        };

        this.formFields = this.formFactory.enrichMetadataFields(meta.fields, relationOptions);
        const baseCols = this.formFactory.getTableColumnsFromMetadata<Investment>(this.formFields);
        this.columns = baseCols.map((col) => {
          if (col.key === 'account_id') return { ...col, formatter: (v: number) => this.accountMap[v] ?? String(v) };
          if (col.key === 'category_id') return { ...col, formatter: (v: number) => this.categoryMap[v] ?? String(v) };
          if (col.key === 'date') return { ...col, formatter: (v: string) => this.utilsService.formatDateLong(v) };
          return col;
        });

        this.isLoading = false;
        this.cdr.detectChanges();
      },
      error: () => {
        this.errorMessage = 'Error loading investments';
        this.isLoading = false;
      },
    });
  }

  editInvestment(investment: Investment): void {
    this.openDialog(investment);
  }

  addInvestment(): void {
    this.openDialog();
  }

  openDialog(data?: Investment): void {
    const dialogRef = this.dialog.open(GenericDialogComponent, {
      data: {
        title: data ? 'Edit Investment' : 'New Investment',
        fields: this.formFields,
        initialData: data || {},
      },
    });

    dialogRef.afterClosed().subscribe((result) => {
      if (result) {
        result.id ? this.updateInvestment(result) : this.createInvestment(result);
      }
    });
  }

  updateInvestment(investment: Investment): void {
    this.investmentService.update(investment.id!, investment).subscribe({
      next: (response: ApiResponse<Investment>) => {
        const updated = response.response;
        const index = this.investments.findIndex((h) => h.id === updated.id);
        if (index !== -1) {
          this.investments[index] = updated;
          this.investments = [...this.investments];
        }
        this.toastService.showToast(response, environment.toastType.Success, {});
        this.cdr.detectChanges();
      },
      error: (err) => {
        this.toastService.showToast(err.error as ApiResponse<string>, environment.toastType.Error, {});
      },
    });
  }

  createInvestment(investment: Investment): void {
    this.investmentService.create(investment).subscribe({
      next: (response: ApiResponse<Investment>) => {
        this.investments.push(response.response);
        this.investments = [...this.investments];
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
