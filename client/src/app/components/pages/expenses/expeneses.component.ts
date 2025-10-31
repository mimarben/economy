import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { forkJoin } from 'rxjs';
import { MatDialog } from '@angular/material/dialog';
import { GenericTableComponent, TableColumn } from '@components/shared/generic-table/generic-table.component';
import { GenericDialogComponent } from '@components/shared/generic-dialog/generic-dialog.component';
import { ToastService } from '@services/toast.service';
import { environment } from '@environments/environment';
import { ApiResponse } from '@models/apiResponse';
import { ExpenseBase as Expense } from '@models/ExpenseBase';
import { FormFieldConfig } from '@components/shared/generic-form/form-config';
import { ExpenseService } from '@services/expense.service';
import { FormFactoryService } from '@factories/forms/form-factory.service';
import { UtilsService } from '@utils/utils.service';
import { ExpenseCategoryService } from '@services/expense-category.service';
import { UserService } from '@services/user.service';
import { AccountService } from '@services/account.service';
import { SourceService } from '@services/source.service';

@Component({
  selector: 'app-expenses-component',
  imports: [GenericTableComponent],
  templateUrl: './expeneses.component.html',
  styleUrl: './expeneses.component.html',
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
      // Observables correctos definidos por el usuario
      const expenses$ = this.expenseService.getAll();
      const users$ = this.userService.getUsers();
      const categories$ = this.expensecategoryService.getAll();
      const sources$ = this.sourceService.getAll();
      const accounts$ = this.accountService.getAll();
      forkJoin([expenses$, users$, categories$, sources$, accounts$]).subscribe({
          next: ([expensesResponse, usersResponse, categoriesResponse, sourcesResponse, accountsResponse]) => {

              this.expenses = expensesResponse.response || [];


              const users = usersResponse.response || [];
              this.usersMap = Object.fromEntries(
                  users.map((u) => [
                      u.id,
                      `${u.name} ${u.surname1} ${u.surname2 || ''}`,
                  ])
              );


              const categories = categoriesResponse.response || [];
              console.log('Categories loaded:', categories);
              this.expensesCategoriesMap = Object.fromEntries(
                categories.map((c) => [c.id, c.name])
              );


              const sources = sourcesResponse.response || [];
              this.sourcesMap = Object.fromEntries(
                  sources.map((s) => [s.id, s.name])
              );

              const accounts = accountsResponse.response || [];
              console.log('Accounts loaded:', accounts);
              this.accountsMap = Object.fromEntries(
                  accounts.map((a) => [a.id, `${a.name}`])
              );
              console.log('Accounts Map:', this.accountsMap);
              console.log('Expenses loaded:', this.expenses);
              this.isLoading = false;
              this.cdr.detectChanges();
          },
          error: (err) => {
              // 4. Error: Manejar cualquier fallo
              console.error('Error al cargar datos:', err);
              // Mensaje de error ajustado para reflejar las entidades cargadas
              this.errorMessage = 'Error loading expense data or related entities (Users, Categories, Sources, Accounts).';
              this.isLoading = false;
          },
      });
  }

  openDialog(data?: Expense): void {
  this.isLoading = true;

  // Creamos los observables de todas las dependencias
  const users$ = this.userService.getUsers();
  const categories$ = this.expensecategoryService.getAll();
  const sources$ = this.sourceService.getAll();
  const accounts$ = this.accountService.getAll();

  // Ejecutamos todas las llamadas en paralelo
  forkJoin([users$, categories$, sources$, accounts$]).subscribe({
    next: ([usersResponse, categoriesResponse, sourcesResponse, accountsResponse]) => {
      // Extraemos los datos (response de cada servicio)
      const users = usersResponse.response || [];
      const categories = categoriesResponse.response || [];
      const sources = sourcesResponse.response || [];
      const accounts = accountsResponse.response || [];

      // Obtenemos la configuración base del formulario
      const baseConfig = this.formFactory.getFormConfig('expense');

      // Enriquecemos los campos select con los datos cargados
      const enrichedConfig = baseConfig.map((field) => {
        switch (field.key) {
          case 'user_id':
            return {
              ...field,
              options: users.map((u) => ({
                value: u.id,
                label: `${u.name} ${u.surname1} ${u.surname2 || ''}`,
              })),
            };
          case 'category_id':
            return {
              ...field,
              options: categories.map((c) => ({
                value: c.id,
                label: c.name,
              })),
            };
          case 'source_id':
            return {
              ...field,
              options: sources.map((s) => ({
                value: s.id,
                label: s.name,
              })),
            };
          case 'account_id':
            return {
              ...field,
              options: accounts.map((a) => ({
                value: a.id,
                label: a.name,
              })),
            };
          default:
            return field;
        }
      });

      // Abrimos el diálogo con los datos enriquecidos
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
      error: (err) => {
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
