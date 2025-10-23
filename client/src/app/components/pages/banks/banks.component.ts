import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';


import { BankBase as Bank } from '../../../models/BankBase';
import { GenericTableComponent, TableColumn } from '../../shared/generic-table/generic-table.component';

import { ApiResponse } from '../../../models/apiResponse';
import { GenericDialogComponent } from '../../shared/generic-dialog/generic-dialog.component';
import { FormFactoryService } from '../../../factories/forms/form-factory.service';
import { BankService } from '../../../services/bank.service';
import { FormFieldConfig } from '../../shared/generic-form/form-config';
import { ToastService } from '../../../services/toast.service';
import { environment } from '../../../../environments/environment';


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

  columns: TableColumn<Bank>[] = [
    { key: 'id', label: 'ID', sortable: true },
    { key: 'name', label: 'Name', sortable: true },
    { key: 'description', label: 'Description', sortable: false },
    { key: 'active',label: 'Active',sortable: true,formatter: (v) => (v ? 'Yes' : 'No')},
  ];


  constructor(
    private bankService: BankService,
    private cdr: ChangeDetectorRef,
    private dialog: MatDialog,
    private toastService: ToastService,
    private formFactory: FormFactoryService
  ) {}

  ngOnInit() {
    this.loadBanks();
    this.loadFormFields();
  }

  private loadFormFields(): void {
    this.formFields = this.formFactory.getFormConfig('bank');
    this.loadBanks();
  }

  loadBanks() {
    this.isLoading = true;
    this.bankService.getBanks().subscribe({
      next: (data: ApiResponse<Bank[]>) => {
        this.banks = data.response;
        this.isLoading = false;
      },
      error: (err) => {
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
        fields: this.formFactory.getFormConfig('bank'),
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
    this.bankService.updateBank(bank.id, bank).subscribe({
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
      error: (error) => {
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
      error: (error) => {
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
