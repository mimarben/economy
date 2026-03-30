import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { forkJoin } from 'rxjs';
import { MatDialog } from '@angular/material/dialog';
import { GenericTableComponent, TableColumn } from '@shared/generic-table/generic-table.component';
import { GenericDialogComponent } from '@shared/generic-dialog/generic-dialog.component';
import { ToastService } from '@core_services/toast.service';
import { environment } from '@env/environment';
import { ApiResponse } from '@core_models/apiResponse';
import { ExpenseBase as Expense } from '@expenses_models/ExpenseBase';
import { UserBase as User } from '@users_models/UserBase';
import { ExpenseCategoryBase as ExpenseCategory } from '@expenses_models/ExpenseCategoryBase';
import { SourceBase as Source } from '@finance_models/SourceBase';
import { AccountBase as Account } from '@finance_models/AccountBase';
import { FormFieldConfig } from '@shared/generic-form/form-config';
import { ExpenseService } from '@expenses_services/expense.service';
import { FormFactoryService } from '@app/core/factories/form-factory.service';
import { UtilsService } from '@app/utils/utils.service';
import { ExpenseCategoryService } from '@expenses_services/expense-category.service';
import { UserService } from '@users_services/user.service';
import { AccountService } from '@finance_services/account.service';
import { SourceService } from '@finance_services/source.service';

@Component({
  selector: 'app-expenses-component',
  imports: [GenericTableComponent],
  templateUrl: './expenses.component.html',
  styleUrl: './expenses.component.css',
})

export class ExpensesComponent implements OnInit {
  expenses: Expense[] = [];
  filterValue = '';
  isLoading = false;
  errorMessage = '';
  formFields: FormFieldConfig[] = [];
  isFormValid = false;
  columns: TableColumn<Expense>[] = [];
  expenseCategoryMap: Record<number, string> = [];
  usersMap: Record<number, string> = {};
  accountsMap: Record<number, string> = {};
  sourcesMap: Record<number, string> = {};
  expensesCategoriesMap: Record<number, string> = {};

  constructor(
    private expenseService: ExpenseService,
    private expensecategoryService: ExpenseCategoryService,
    private utilsService: UtilsService,
    private cdr: ChangeDetectorRef,
    private dialog: MatDialog,
    private toastService: ToastService,
    private formFactory: FormFactoryService,
    private userService: UserService,
    private accountService: AccountService,
    private sourceService: SourceService
  ) {}

  ngOnInit(): void {
    this.formFields = this.formFactory.getFormConfig('expense');
    this.columns = this.formFactory.getTableColumns<Expense>('expense', {
      category_id: (value: number) =>this.expensesCategoriesMap[value] ?? value,
      user_id: (value: number) => this.usersMap[value] ?? value,
      source_id: (value: number) => this.sourcesMap[value] ?? value,
      account_id: (value: number) => this.accountsMap[value] ?? value,
      date: (value: string) => this.utilsService.formatDateShortStr(value),
    });
    this.loadExpenses();
  }

  loadExpenses() {
      this.isLoading = true;
      this.errorMessage = '';
      // Load all required resources in parallel
      const expenses$ = this.expenseService.getAll();
      const users$ = this.userService.getUsers();
      const categories$ = this.expensecategoryService.getAll();
      const sources$ = this.sourceService.getAll();
      const accounts$ = this.accountService.getAll();
      forkJoin([expenses$, users$, categories$, sources$, accounts$]).subscribe({
          next: ([expensesResponse, usersResponse, categoriesResponse, sourcesResponse, accountsResponse]) => {

              this.expenses = expensesResponse.response || [];


              const users = usersResponse?.response || [];
              this.usersMap = Object.fromEntries(
                  users.map((u: User) => [
                      u.id,
                      `${u.name} ${u.surname1} ${u.surname2 || ''}`,
                  ])
              );


              const categories = categoriesResponse?.response || [];
              console.log('Categories loaded:', categories);
              this.expensesCategoriesMap = Object.fromEntries(
                categories.map((c: ExpenseCategory) => [c.id, c.name])
              );


              const sources = sourcesResponse?.response || [];
              this.sourcesMap = Object.fromEntries(
                  sources.map((s: Source) => [s.id, s.name])
              );

              const accounts = accountsResponse?.response || [];
              console.log('Accounts loaded:', accounts);
              this.accountsMap = Object.fromEntries(
                  accounts.map((a: Account) => [a.id, `${a.name}`])
              );
              console.log('Accounts Map:', this.accountsMap);
              console.log('Expenses loaded:', this.expenses);
              this.isLoading = false;
              this.cdr.detectChanges();
          },
          error: (err: any) => {
              // Handle any failure during parallel loading
              console.error('Error loading data:', err);
              this.errorMessage = 'Error loading expense data or related entities (Users, Categories, Sources, Accounts).';
              this.isLoading = false;
          },
      });
  }

  openDialog(data?: Expense): void {
  this.isLoading = true;

  // Build observables for all dependencies
  const users$ = this.userService.getUsers();
  const categories$ = this.expensecategoryService.getAll();
  const sources$ = this.sourceService.getAll();
  const accounts$ = this.accountService.getAll();

  // Execute all requests in parallel
  forkJoin([users$, categories$, sources$, accounts$]).subscribe({
    next: ([usersResponse, categoriesResponse, sourcesResponse, accountsResponse]) => {
      // Extract payloads from each service response
      const users = usersResponse?.response || [];
      const categories = categoriesResponse?.response || [];
      const sources = sourcesResponse?.response || [];
      const accounts = accountsResponse?.response || [];

      // Get base form configuration
      const baseConfig = this.formFactory.getFormConfig('expense');

      // Populate select fields with loaded data
      const enrichedConfig = baseConfig.map((field: FormFieldConfig) => {
        switch (field.key) {
          case 'user_id':
            return {
              ...field,
              options: users.map((u: User) => ({
                value: u.id,
                label: `${u.name} ${u.surname1} ${u.surname2 || ''}`,
              })),
            };
          case 'category_id':
            return {
              ...field,
              options: categories.map((c: ExpenseCategory) => ({
                value: c.id,
                label: c.name,
              })),
            };
          case 'source_id':
            return {
              ...field,
              options: sources.map((s: Source) => ({
                value: s.id,
                label: s.name,
              })),
            };
          case 'account_id':
            return {
              ...field,
              options: accounts.map((a: Account) => ({
                value: a.id,
                label: a.name,
              })),
            };
          default:
            return field;
        }
      });

      // Open dialog using enriched config
      const dialogRef = this.dialog.open(GenericDialogComponent, {
        data: {
          title: data ? 'Edit Expense' : 'New Expense',
          fields: enrichedConfig,
          initialData: data || {},
        },
      });

      dialogRef.afterClosed().subscribe((result) => {
        if (result) {
          result.id ? this.update(result) : this.create(result);
        }
      });

      this.isLoading = false;
      this.cdr.detectChanges();
    },
    error: (error) => {
      this.errorMessage = 'Error loading expenses data or related entities (Users, Categories, Sources, Accounts).';
      this.isLoading = false;
    },
  });
}


  edit(expense: Expense): void {
    this.openDialog(expense);
  }

  add(): void {
    this.openDialog();
  }

  update(expense: Expense): void {
   /*  this.expenseService.update(expense.id, expense).subscribe({
      next: (response: ApiResponse<Expense>) => {
        const updated = response.response;
        const index = this.expenses.findIndex((h) => h.id === updated.id);
        if (index !== -1) {
          this.expenses[index] = updated;
          this.expenses = [...this.expenses];
        }
        this.toastService.showToast(
          response,
          environment.toastType.Success,
          {}
        );
        this.cdr.detectChanges();
      },
      error: (err) => {
        this.toastService.showToast(
          err.error as ApiResponse<string>,
          environment.toastType.Error,
          {}
        );
      },
    }); */
  }

  create(expense: Expense): void {
    this.expenseService.create(expense).subscribe({
      next: (response: ApiResponse<Expense>) => {
        this.expenses.push(response.response);
        this.expenses = [...this.expenses];
        this.toastService.showToast(
          response,
          environment.toastType.Success,
          {}
        );
        this.cdr.detectChanges();
      },
      error: (err: any) => {
        this.toastService.showToast(
          err.error as ApiResponse<string>,
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
