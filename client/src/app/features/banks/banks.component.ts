import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { BankBase as Bank } from '@finance_models/BankBase';
import { GenericTableComponent, TableColumn } from '@shared/generic-table/generic-table.component';
import { ApiResponse } from '@app/models/core/APIResponse';
import { GenericDialogComponent } from '@shared/generic-dialog/generic-dialog.component';
import { FormFactoryService } from '@app/core/factories/form-factory.service';
import { BankService } from '@finance_services/bank.service';
import { FormFieldConfig } from '@shared/generic-form/form-config';
import { ToastService } from '@core_services/toast.service';
import { environment } from '@env/environment';
import { MetaService } from '@core_services/meta.service';
import { forkJoin } from 'rxjs';


@Component({
  selector: 'app-accounts',
  imports: [GenericTableComponent],
  templateUrl: './banks.component.html',
  styleUrls: ['./banks.component.css'],
})
export class BanksComponent implements OnInit {
  banks: Bank[] = [];
  filterValue = '';
  isLoading = false;
  errorMessage = '';
  formFields: FormFieldConfig[] = [];
  isFormValid = false;

  columns: TableColumn<Bank>[] = [];


  constructor(
    private bankService: BankService,
    private cdr: ChangeDetectorRef,
    private dialog: MatDialog,
    private toastService: ToastService,
    private formFactory: FormFactoryService,
    private metaService: MetaService,
  ) {}

  ngOnInit() {
    this.loadInitialData();
  }

  private loadInitialData(): void {
    this.isLoading = true;
    forkJoin({
      banks: this.bankService.getBanks(),
      meta: this.metaService.getMeta('bank'),
    }).subscribe({
      next: ({ banks, meta }) => {
        this.banks = banks.response;
        this.formFields = this.formFactory.enrichMetadataFields(meta.fields);
        this.columns = this.formFactory.getTableColumnsFromMetadata<Bank>(this.formFields);
        this.isLoading = false;
      },
      error: () => {
        this.errorMessage = 'Error loading banks';
        this.isLoading = false;
      },
    });
  }

  editBank(bank: Bank): void {
    this.openDialog(bank);
  }

  addBank(): void {
    this.openDialog();
  }

  openDialog(data?: Bank): void {
    const dialogRef = this.dialog.open(GenericDialogComponent, {
      data: {
        title: data ? 'Edit Bank' : 'New Bank',
        fields: this.formFields,
        initialData: data || {},
      },
    });

    dialogRef.afterClosed().subscribe((result) => {
      if (result) {
        result.id ? this.updateBank(result) : this.createBank(result);
      }
    });
  }

  updateBank(bank: Bank): void {
    this.bankService.updateBank(bank.id!, bank).subscribe({
      next: (response: ApiResponse<Bank>) => {
        this.isLoading = false;
        this.toastService.showToast(
          response,
          environment.toastType.Success,
          {}
        );
        const updatedBank = response.response;
        const index = this.banks.findIndex((acc) => acc.id === updatedBank.id);
        if (index !== -1) {
          this.banks[index] = updatedBank;
          this.banks = [...this.banks]; // Reassign to trigger change detection
        }
        this.cdr.detectChanges();
      },
      error: (error: any) => {
        console.error('Error updating account:', error.error);
        this.isLoading = false;
        this.toastService.showToast(
          error.error as ApiResponse<string>,
          environment.toastType.Error,
          {}
        );
      },
    });
  }

  createBank(bank: Bank): void {
    this.bankService.createBank(bank).subscribe({
      next: (response: ApiResponse<Bank>) => {
        this.isLoading = false;
        this.toastService.showToast(
          response,
          environment.toastType.Success,
          {}
        );
        const newBank = response.response;
        this.banks.push(newBank); // Add the new bank to the array
        this.banks = [...this.banks]; // Reassign to trigger change detection
        this.cdr.detectChanges();
      },
      error: (error: any) => {
        console.error('Error creating bank:', error.error);
        this.isLoading = false;
        this.errorMessage = 'Failed to create bank.';
        this.toastService.showToast(
          error.error as ApiResponse<string>,
          environment.toastType.Error,
          {}
        );
      },
    });
  }

  applyFilter(event: Event) {
    this.filterValue = (event.target as HTMLInputElement).value
      .trim()
      .toLowerCase();
  }
}
