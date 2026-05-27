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
import { SavingBase as Saving } from '@savings_models/SavingBase';
import { AccountBase as Account } from '@finance_models/AccountBase';
import { SavingService } from '@savings_services/saving.service';
import { AccountService } from '@finance_services/account.service';
import { MetaService } from '@core_services/meta.service';
import { UtilsService } from '@app/utils/utils.service';

@Component({
  selector: 'app-savings',
  imports: [GenericTableComponent],
  templateUrl: './savings.component.html',
  styleUrl: './savings.component.css',
})
export class SavingsComponent implements OnInit {
  savings: Saving[] = [];
  filterValue = '';
  isLoading = false;
  errorMessage = '';
  formFields: FormFieldConfig[] = [];
  isFormValid = false;
  columns: TableColumn<Saving>[] = [];
  accountsMap: Record<number, string> = {};

  constructor(
    private savingService: SavingService,
    private accountService: AccountService,
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
      savings: this.savingService.getAll(),
      meta: this.metaService.getMeta('saving'),
      accounts: this.accountService.getAll(),
    }).subscribe({
      next: ({ savings, meta, accounts }) => {
        this.savings = savings.response;

        this.accountsMap = Object.fromEntries(
          accounts.response.map((a: Account) => [a.id as number, a.name])
        );

        const relationOptions = {
          account: accounts.response.map((a: Account) => ({ value: a.id as number, label: a.name })),
        };

        this.formFields = this.formFactory.enrichMetadataFields(meta.fields, relationOptions);
        const baseCols = this.formFactory.getTableColumnsFromMetadata<Saving>(this.formFields);
        this.columns = baseCols.map((col) => {
          if (col.key === 'account_id') return { ...col, formatter: (v: number) => this.accountsMap[v] ?? String(v) };
          if (col.key === 'date') return { ...col, formatter: (v: string) => this.utilsService.formatDateLong(v) };
          return col;
        });

        this.isLoading = false;
      },
      error: () => {
        this.errorMessage = 'Error loading savings';
        this.isLoading = false;
      },
    });
  }

  editSaving(saving: Saving): void {
    this.openDialog(saving);
  }

  addSaving(): void {
    this.openDialog();
  }

  openDialog(data?: Saving): void {
    const dialogRef = this.dialog.open(GenericDialogComponent, {
      data: {
        title: data ? 'Edit Saving' : 'New Saving',
        fields: this.formFields,
        initialData: data || {},
      },
    });

    dialogRef.afterClosed().subscribe((result) => {
      if (result) {
        result.id ? this.updateSaving(result) : this.createSaving(result);
      }
    });
  }

  updateSaving(saving: Saving): void {
    this.savingService.update(saving.id!, saving).subscribe({
      next: (response: ApiResponse<Saving>) => {
        const updated = response.response;
        const index = this.savings.findIndex((s) => s.id === updated.id);
        if (index !== -1) {
          this.savings[index] = updated;
          this.savings = [...this.savings];
        }
        this.toastService.showToast(response, environment.toastType.Success, {});
        this.cdr.detectChanges();
      },
      error: (err: any) => {
        this.toastService.showToast(err.error as ApiResponse<string>, environment.toastType.Error, {});
      },
    });
  }

  createSaving(saving: Saving): void {
    this.savingService.create(saving).subscribe({
      next: (response: ApiResponse<Saving>) => {
        this.savings.push(response.response);
        this.savings = [...this.savings];
        this.toastService.showToast(response, environment.toastType.Success, {});
        this.cdr.detectChanges();
      },
      error: (err: any) => {
        this.toastService.showToast(err.error as ApiResponse<string>, environment.toastType.Error, {});
      },
    });
  }

  applyFilter(event: Event) {
    this.filterValue = (event.target as HTMLInputElement).value.trim().toLowerCase();
  }
}
