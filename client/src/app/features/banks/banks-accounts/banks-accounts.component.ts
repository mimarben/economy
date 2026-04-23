import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { forkJoin } from 'rxjs';
import { AccountBase as Account } from '@finance_models/AccountBase';
import { BankBase as Bank } from '@finance_models/BankBase';
import { UserBase as User } from '@users_models/UserBase';
import { GenericTableComponent, TableColumn } from '@shared/generic-table/generic-table.component';
import { AccountService } from '@finance_services/account.service';
import { ApiResponse } from '@app/models/core/APIResponse';
import { GenericDialogComponent } from '@shared/generic-dialog/generic-dialog.component';
import { FormFactoryService } from '@app/core/factories/form-factory.service';
import { BankService } from '@finance_services/bank.service';
import { UserService } from '@users_services/user.service';
import { FormFieldConfig } from '@shared/generic-form/form-config';
import { ToastService } from '@core_services/toast.service';
import { environment } from '@env/environment';
import { MetaService } from '@core_services/meta.service';
import { ImportOriginBase as ImportOrigin } from '@import_models/import-originBase';
import { ImportProfileBase as ImportProfile } from '@import_models/import-profileBase';
import { ImportOriginsService, ImportProfilesService } from '@import_services/import-profiles.service';

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
  origins: ImportOrigin[] = [];
  profiles: ImportProfile[] = [];
  columns: TableColumn<Account>[] = [];

  constructor(
    private accountService: AccountService,
    private bankService: BankService,
    private userService: UserService,
    private cdr: ChangeDetectorRef,
    private dialog: MatDialog,
    private toastService: ToastService,
    private formFactory: FormFactoryService,
    private metaService: MetaService,
    private importOriginsService: ImportOriginsService,
    private importProfilesService: ImportProfilesService,
  ) {}

  ngOnInit() {
    this.loadInitialData();
  }

  private loadInitialData(): void {
    this.isLoading = true;
    forkJoin({
      accounts: this.accountService.getAll(),
      banks: this.bankService.getBanks(),
      users: this.userService.getUsers(),
      origins: this.importOriginsService.getOrigins(),
      profiles: this.importProfilesService.getProfiles(),
      meta: this.metaService.getMeta('account'),
    }).subscribe({
      next: ({ accounts, banks, users, origins, profiles, meta }) => {
        this.accounts = accounts.response as Account[];
        this.banks = banks.response;
        this.users = users.response;
        this.origins = origins.response;
        this.profiles = profiles.response;

        this.formFields = this.formFactory.enrichMetadataFields(meta.fields, {
          bank: this.banks.map((bank) => ({ value: bank.id!, label: bank.name })),
          bank_id: this.banks.map((bank) => ({ value: bank.id!, label: bank.name })),
          user: this.users.map((user) => ({ value: user.id!, label: `${user.name} (${user.email})` })),
          user_ids: this.users.map((user) => ({ value: user.id!, label: `${user.name} (${user.email})` })),
          'import-origin': this.origins.map((origin) => ({ value: origin.id, label: origin.name })),
          import_origin_id: this.origins.map((origin) => ({ value: origin.id, label: origin.name })),
          'import-profile': this.profiles.map((profile) => ({ value: profile.id, label: profile.name })),
          import_profile_id: this.profiles.map((profile) => ({ value: profile.id, label: profile.name })),
        }).map((field) => {
          if (field.key !== 'user_ids') {
            return field;
          }
          return {
            ...field,
            label: 'Usuarios de la cuenta',
            multiple: true,
          };
        });

        this.columns = this.formFactory.getTableColumnsFromMetadata<Account>(this.formFields).map((column) => {
          if (column.key === 'bank_id') {
            return {
              ...column,
              formatter: (value: number) => this.getBankName(value),
            };
          }

          if (column.key === 'users') {
            return {
              ...column,
              label: 'Usuarios',
              formatter: (value: any[]) => this.formatUsers(value),
            };
          }

          if (column.key === 'iban') {
            return {
              ...column,
              label: 'IBAN',
            };
          }

          return column;
        });

        this.isLoading = false;
      },
      error: () => {
        this.errorMessage = 'Error loading accounts';
        this.isLoading = false;
      },
    });
  }
  getBankName(bankId: number): string {
    const bank = this.banks.find(b => b.id === bankId);
    return bank?.name || 'Unknown Bank';
  }
  formatUsers(users: any[]): string {
    if (!users || users.length === 0) return 'No users';
    return users
      .map((user) => `${user.name} ${user.surname1}`)
      .join(', ');
  }

  editAccount(account: Account): void {
    this.openDialog(account);
  }

  addAccount(): void {
    this.openDialog();
  }

  openDialog(data?: Account): void {
    const initialData = data
      ? {
          ...data,
          user_ids: (data.users ?? [])
            .map((user) => user.id)
            .filter((id): id is number => typeof id === 'number'),
        }
      : {};
    const dialogRef = this.dialog.open(GenericDialogComponent, {
      data: {
        title: data ? 'Edit Account' : 'New Account',
        fields: this.formFields,
        initialData,
      }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        const payload = this.normalizeAccountPayload(result);
        payload.id ? this.updateAccount(payload) : this.createAccount(payload);
      }
    });
  }
  updateAccount(account: Account): void {
    this.accountService.update(account.id!, account).subscribe({
      next: (response: ApiResponse<Account>) => {
        this.isLoading = false;
        this.toastService.showToast(response, environment.toastType.Success, {});
        const index = this.accounts.findIndex(acc => acc.id === response.response.id);
        if (index !== -1) {
          this.accounts[index] = response.response;
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
    this.accountService.create(account).subscribe({
      next: (response: ApiResponse<Account>) => {
        this.isLoading = false;
        this.toastService.showToast(response, environment.toastType.Success, {});
        this.accounts.push(response.response); // Add the new account to the array
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

  private normalizeAccountPayload(account: Account): Account {
    // Asegúrate de que user_ids es un array
    if (!Array.isArray(account.user_ids)) {
      account.user_ids = [];
    }
    return account;
  }
}
