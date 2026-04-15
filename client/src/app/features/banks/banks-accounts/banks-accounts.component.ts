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

type AccountWithUsers = Account & {
  users?: User[];
  user_ids?: number[];
};

@Component({
  selector: 'app-banks-accounts',
  imports: [GenericTableComponent],
  templateUrl: './banks-accounts.component.html',
  styleUrl: './banks-accounts.component.css'
})
export class BanksAccountsComponent implements OnInit {
  accounts: AccountWithUsers[] = [];
  filterValue = '';
  isLoading = false;
  errorMessage = '';
  formFields: FormFieldConfig[] = [];
  isFormValid = false;
  banks: Bank[] = [];
  users: User[] = [];
  origins: ImportOrigin[] = [];
  profiles: ImportProfile[] = [];
  columns: TableColumn<AccountWithUsers>[] = [];

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
        this.accounts = (accounts.response as AccountWithUsers[]).map((account) => {
          const relationUserIds = (account.users ?? [])
            .map((user) => user.id)
            .filter((id): id is number => typeof id === 'number');
          return {
            ...account,
            user_ids: relationUserIds.length > 0
              ? relationUserIds
              : (typeof account.user_id === 'number' ? [account.user_id] : []),
          };
        });
        this.banks = banks.response;
        this.users = users.response;
        this.origins = origins.response;
        this.profiles = profiles.response;

        this.formFields = this.formFactory.enrichMetadataFields(meta.fields, {
          bank: this.banks.map((bank) => ({ value: bank.id!, label: bank.name })),
          bank_id: this.banks.map((bank) => ({ value: bank.id!, label: bank.name })),
          user: this.users.map((user) => ({ value: user.id!, label: `${user.name} (${user.email})` })),
          user_id: this.users.map((user) => ({ value: user.id!, label: `${user.name} (${user.email})` })),
          'import-origin': this.origins.map((origin) => ({ value: origin.id, label: origin.name })),
          import_origin_id: this.origins.map((origin) => ({ value: origin.id, label: origin.name })),
          'import-profile': this.profiles.map((profile) => ({ value: profile.id, label: profile.name })),
          import_profile_id: this.profiles.map((profile) => ({ value: profile.id, label: profile.name })),
        }).map((field) => {
          if (field.key !== 'user_id') {
            return field;
          }
          return {
            ...field,
            label: 'Usuarios de la cuenta',
            multiple: true,
          };
        });

        this.columns = this.formFactory.getTableColumnsFromMetadata<AccountWithUsers>(this.formFields).map((column) => {
          if (column.key === 'bank_id') {
            return {
              ...column,
              formatter: (value: number) => this.getBankName(value),
            };
          }

          if (column.key === 'user_id') {
            return {
              ...column,
              formatter: (value: number | number[]) => this.getUserNames(value),
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
  getUserNames(userId: number | number[]): string {
    if (Array.isArray(userId)) {
      const names = userId
        .map((id) => this.getUserNames(id))
        .filter((name) => name !== 'Unknown User');
      return names.length ? names.join(', ') : 'Unknown User';
    }
    const user = this.users.find(u => u.id === userId);
    return user ? `${user.name} ${user.surname1} ${user.surname2}` : 'Unknown User';
  }

  editAccount(account: AccountWithUsers): void {
    this.openDialog(account);
  }

  addAccount(): void {
    this.openDialog();
  }
  openDialog(data?: AccountWithUsers): void {
    const initialData = data
      ? {
          ...data,
          user_id: data.user_ids?.length
            ? data.user_ids
            : (typeof data.user_id === 'number' ? [data.user_id] : []),
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

  updateAccount(account: AccountWithUsers): void {
    this.accountService.update(account.id!, account).subscribe({
      next: (response: ApiResponse<AccountWithUsers>) => {
        this.isLoading = false;
        this.toastService.showToast(response, environment.toastType.Success, {});
        const updatedAccount = this.attachUserIds(response.response);
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

  createAccount(account: AccountWithUsers): void {
    this.accountService.create(account).subscribe({
      next: (response: ApiResponse<AccountWithUsers>) => {
        this.isLoading = false;
        this.toastService.showToast(response, environment.toastType.Success, {});
        const newAccount = this.attachUserIds(response.response);
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

  private normalizeAccountPayload(account: AccountWithUsers): AccountWithUsers {
    const userIds = Array.isArray(account.user_id)
      ? account.user_id.filter((id): id is number => typeof id === 'number')
      : (Array.isArray(account.user_ids) ? account.user_ids : [account.user_id])
          .filter((id): id is number => typeof id === 'number');

    return {
      ...account,
      user_id: userIds[0] ?? account.user_id,
      user_ids: userIds,
    };
  }

  private attachUserIds(account: AccountWithUsers): AccountWithUsers {
    const usersFromRelation = account.users
      ?.map((user) => user.id)
      .filter((id): id is number => typeof id === 'number');

    return {
      ...account,
      user_ids: usersFromRelation?.length
        ? usersFromRelation
        : (typeof account.user_id === 'number' ? [account.user_id] : []),
    };
  }
}
