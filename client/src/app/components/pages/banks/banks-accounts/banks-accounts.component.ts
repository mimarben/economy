import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { forkJoin } from 'rxjs';
import { AccountBase as Account } from '../../../../models/AccountBase';
import { BankBase as Bank } from '../../../../models/BankBase';
import { UserBase as User } from '../../../../models/UserBase';
import { GenericTableComponent, TableColumn } from '../../../shared/generic-table/generic-table.component';
import { AccountService } from '../../../../services/account.service';
import { ApiResponse } from '../../../../models/apiResponse';
import { GenericDialogComponent } from '../../../shared/generic-dialog/generic-dialog.component';
import { FormFactoryService } from '../../../../factories/forms/form-factory.service';
import { BankService } from '../../../../services/bank.service';
import { UserService } from '../../../../services/user.service';
import { FormFieldConfig } from '../../../shared/generic-form/form-config';
import { ToastService } from '../../../../services/toast.service';
import { environment } from '../../../../../environments/environment';

@Component({
  selector: 'app-banks-accounts',
  imports: [GenericTableComponent],
  templateUrl: './banks-accounts.component.html',
  styleUrl: './banks-accounts.component.css'
})
export class BanksAccountsComponent implements OnInit {
  accounts: Account[] = [];
  filterValue = '';
  isLoading = false;
  errorMessage = '';
  formFields: FormFieldConfig[] = [];
  isFormValid = false;
  banks: Bank[] = [];
  users: User[] = [];
  columns: TableColumn<Account>[] = [
    { key: 'id', label: 'ID', sortable: true },
    { key: 'name', label: 'Name', sortable: true },
    { key: 'description', label: 'Description', sortable: false },
    { key: 'iban', label: 'IBAN', sortable: true },
    { key: 'balance', label: 'Balance', sortable: true },
    { key: 'active', label: 'Active', sortable: true, formatter: (v) => v ? 'Yes' : 'No' },
    { key: 'bank_id', label: 'Bank-ID', sortable: true, formatter: (v: number) => this.getBankName(v) },
    { key: 'user_id', label: 'User-ID', sortable: true, formatter: (v: number) => this.getUserName(v) },
  ];

  constructor(
    private accountService: AccountService,
    private bankService: BankService,
    private userService: UserService,
    private cdr: ChangeDetectorRef,
    private dialog: MatDialog,
    private toastService: ToastService,
    private formFactory: FormFactoryService
  ) {}

  ngOnInit() {
    this.loadAccounts();
    this.loadFormFields();
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
  getBankName(bankId: number): string {
    const bank = this.banks.find(b => b.id === bankId);
    return bank?.name || 'Unknown Bank';
  }
  getUserName(userId: number): string {
  const user = this.users.find(u => u.id === userId);
  return user ? `${user.name} ${user.surname1} ${user.surname2}` : 'Unknown User';
  }
  private loadFormFields(): void {
    this.formFields = this.formFactory.getFormConfig('account');
    this.loadBanks();
    this.loadUsers();
  }

private loadBanks(): void {
  this.bankService.getBanks().subscribe({
    next: (res: ApiResponse<Bank[]>) => {
      this.banks = res.response; // Store banks
      // ... existing form field update code
      this.accounts = [...this.accounts]; // Refresh table
    },
    // ... error handling
  });
}

private loadUsers(): void {
  this.userService.getUsers().subscribe({
    next: (res: ApiResponse<User[]>) => {
      this.users = res.response; // Store users
      // ... existing form field update code
      this.accounts = [...this.accounts]; // Refresh table
    },
    // ... error handling
  });
}

  editAccount(account: Account): void {
    this.openDialog(account);
  }

  addAccount(): void {
    this.openDialog();
  }
openDialog(data?: Account): void {
  // Cargar bancos y usuarios en paralelo
  forkJoin({
    banks: this.bankService.getBanks(),
    users: this.userService.getUsers()
  }).subscribe({
    next: (responses) => {
      // Obtener configuración base del formulario
      const baseConfig = this.formFactory.getFormConfig('account');

      // Enriquecer los campos select con las opciones
      const enrichedConfig = baseConfig.map(field => {
        if (field.key === 'bank_id') {
          return {
            ...field,
            options: responses.banks.response.map(bank => ({
              value: bank.id,
              label: bank.name
            }))
          };
        }

        if (field.key === 'user_id') {
          return {
            ...field,
            options: responses.users.response.map(user => ({
              value: user.id,
              label: `${user.name} (${user.email})`
            }))
          };
        }
        return field;
      });

      // Abrir el diálogo con la configuración enriquecida
      const dialogRef = this.dialog.open(GenericDialogComponent, {
        data: {
          title: data ? 'Edit Account' : 'New Account',
          fields: enrichedConfig,
          initialData: data || {}
        }
      });

      dialogRef.afterClosed().subscribe(result => {
        if (result) {
          result.id ? this.updateAccount(result) : this.createAccount(result);
        }
      });
    },
    error: (error) => {
      console.error('Error loading banks and users:', error);
      // Opcional: Mostrar un snackbar o mensaje de error
    }
  });
}
/*  openDialog(data?: Account): void {
    const dialogRef = this.dialog.open(GenericDialogComponent, {
      data: {
        title: data ? 'Edit Account' : 'New Account',
        fields: this.formFactory.getFormConfig('account'),
        initialData: data || {}
      }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        result.id ? this.updateAccount(result) : this.createAccount(result);
      }
    });
  } */

  updateAccount(account: Account): void {
    this.accountService.updateAccount(account.id, account).subscribe({
      next: (response: ApiResponse<Account>) => {
        this.isLoading = false;
        this.toastService.showToast(response, environment.toastType.Success, {});
        const updatedAccount = response.response;
        const index = this.accounts.findIndex(acc => acc.id === updatedAccount.id);
        if (index !== -1) {
          this.accounts[index] = updatedAccount;
          this.accounts = [...this.accounts]; // Reassign to trigger change detection
        }
        this.cdr.detectChanges();
      },
      error: (error) => {
        console.error('Error updating account:', error.error);
        this.isLoading = false;
        this.toastService.showToast(error.error as ApiResponse<string>, environment.toastType.Error, {});
      }
    });
  }

  createAccount(account: Account): void {
    this.accountService.createAccount(account).subscribe({
      next: (response: ApiResponse<Account>) => {
        this.isLoading = false;
        this.toastService.showToast(response, environment.toastType.Success, {});
        const newAccount = response.response;
        this.accounts.push(newAccount); // Add the new account to the array
        this.accounts = [...this.accounts]; // Reassign to trigger change detection
        this.cdr.detectChanges();
      },
      error: (error) => {
        console.error('Error creating account:', error.error);
        this.isLoading = false;
        this.errorMessage = 'Failed to create account.';
        this.toastService.showToast(error.error as ApiResponse<string>, environment.toastType.Error, {});
      }
    });
  }

  applyFilter(event: Event) {
    this.filterValue = (event.target as HTMLInputElement).value.trim().toLowerCase();
  }
}
