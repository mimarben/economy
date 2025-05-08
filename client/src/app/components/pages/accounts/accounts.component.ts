import { Component, OnInit, ChangeDetectorRef } from '@angular/core';

import { AccountBase as Account } from '../../../models/AccountBase';
import { GenericTableComponent, TableColumn } from '../../shared/generic-table/generic-table.component'; // Ajusta la ruta según tu estructura
import { AccountService } from '../../../services/account.service';
import { ApiResponse } from '../../../models/apiResponse';
import { FormFactoryService } from '../../shared/forms/form-factory.service';
import { GenericDialogComponent } from '../../shared/forms/generic-dialog/generic-dialog.component';
@Component({
  selector: 'app-accounts',
  imports: [GenericTableComponent],
  templateUrl: './accounts.component.html',
  styleUrls: ['./accounts.component.css']
})
export class AccountsComponent implements OnInit {
  accounts: Account[] = [];
  filterValue = '';
  isLoading = false;
  errorMessage = '';

  columns: TableColumn<Account>[] = [
    { key: 'id', label: 'ID', sortable: true },
    { key: 'name', label: 'Name', sortable: true },
    { key: 'description', label: 'Description', sortable: false },
    { key: 'iban', label: 'IBAN', sortable: true },
    { key: 'balance', label: 'Balance', sortable: true },
    { key: 'active', label: 'Active', sortable: true, formatter: (v) => v ? 'Yes' : 'No' },
    { key: 'bank_id', label: 'Bank ID', sortable: true },
    { key: 'user_id', label: 'User ID', sortable: true },
  ];

  constructor(private accountService: AccountService,
              private cdr: ChangeDetectorRef){}

  ngOnInit() {
    this.loadAccounts();
  }

  loadAccounts() {
    this.isLoading = true;
    this.accountService.getAccounts().subscribe({
      next: (data: ApiResponse<Account[]>) => {
        this.accounts = data.response;
        this.isLoading = false;
      },
      error: (err) => {
        this.errorMessage = 'Error loading accounts';
        this.isLoading = false;
      },
    });
  }
  editAccount(account: Account): void {
    this.openDialog(account);
  }

  addAccount(): void {
    this.openDialog();
  }

  openDialog(data?: Account): void {
    const dialogRef = this.dialog.open(GenericDialogComponent, {
      data: {
        title: data ? 'Edit Account' : 'New Account',
        fields: this.formFactory.getFormConfig('account'),
        initialData: data || {}
      }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        // Guardar en el backend y actualizar la tabla
      }
    });
  }

  applyFilter(event: Event) {
    this.filterValue = (event.target as HTMLInputElement).value.trim().toLowerCase();
    this.cdr.detectChanges(); // Trigger change detection if needed
  }

}
