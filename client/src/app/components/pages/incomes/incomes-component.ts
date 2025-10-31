import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { forkJoin } from 'rxjs';
import { MatDialog } from '@angular/material/dialog';
import { GenericTableComponent, TableColumn } from '@components/shared/generic-table/generic-table.component';
import { GenericDialogComponent } from '@components/shared/generic-dialog/generic-dialog.component';
import { ToastService } from '@services/toast.service';
import { environment } from '@environments/environment';
import { ApiResponse } from '@models/apiResponse';
import { IncomeBase as Income } from '@models/IncomeBase';
import { IncomeCategoryBase as IncomeCategory } from '@app/models/IncomeCategoryBase';
import { FormFieldConfig } from '@components/shared/generic-form/form-config';
import { IncomeService } from '@services/income.service';
import { FormFactoryService } from '@factories/forms/form-factory.service';
import { UtilsService } from '@utils/utils.service';
import { IncomeCategoryService } from '@services/income-category.service';
import { UserService } from '@services/user.service';
import { AccountService } from '@services/account.service';
import { SourceService } from '@services/source.service';

@Component({
  selector: 'app-incomes-component',
  imports: [GenericTableComponent],
  templateUrl: './incomes-component.html',
  styleUrl: './incomes-component.css',
})
export class IncomesComponent implements OnInit {
  incomes: Income[] = [];
  filterValue = '';
  isLoading = false;
  errorMessage = '';
  formFields: FormFieldConfig[] = [];
  isFormValid = false;
  columns: TableColumn<Income>[] = [];
  incomeCategoryMap: Record<number, string> = [];
  usersMap: Record<number, string> = {};
  accountsMap: Record<number, string> = {};
  sourcesMap: Record<number, string> = {};
  incomesCategoriesMap: Record<number, string> = {};

  constructor(
    private incomeService: IncomeService,
    private incomecategoryService: IncomeCategoryService,
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
    this.formFields = this.formFactory.getFormConfig('income');
    this.columns = this.formFactory.getTableColumns<Income>('income', {
      category_id: (value: number) =>this.incomesCategoriesMap[value] ?? value,
      user_id: (value: number) => this.usersMap[value] ?? value,
      source_id: (value: number) => this.sourcesMap[value] ?? value,
      account_id: (value: number) => this.accountsMap[value] ?? value,
      date: (value: string) => this.utilsService.formatDateShortStr(value),
    });
    this.loadIncomes();
  }

  loadIncomes() {
      this.isLoading = true;
      this.errorMessage = '';
      // Observables correctos definidos por el usuario
      const incomes$ = this.incomeService.getAll();
      const users$ = this.userService.getUsers();
      const categories$ = this.incomecategoryService.getAll();
      const sources$ = this.sourceService.getAll();
      const accounts$ = this.accountService.getAll();
      forkJoin([incomes$, users$, categories$, sources$, accounts$]).subscribe({
          next: ([incomesResponse, usersResponse, categoriesResponse, sourcesResponse, accountsResponse]) => {

              this.incomes = incomesResponse.response || [];


              const users = usersResponse.response || [];
              this.usersMap = Object.fromEntries(
                  users.map((u) => [
                      u.id,
                      `${u.name} ${u.surname1} ${u.surname2 || ''}`,
                  ])
              );


              const categories = categoriesResponse.response || [];
              this.incomesCategoriesMap = Object.fromEntries(
                  categories.map((c) => [c.id, c.name])
              );


              const sources = sourcesResponse.response || [];
              this.sourcesMap = Object.fromEntries(
                  sources.map((s) => [s.id, s.name])
              );

              const accounts = accountsResponse.response || [];
              this.accountsMap = Object.fromEntries(
                  accounts.map((a) => [a.id, `${a.name}`])
              );
              this.isLoading = false;
              this.cdr.detectChanges();
          },
          error: (err) => {
              this.errorMessage = 'Error loading income data or related entities (Users, Categories, Sources, Accounts).';
              this.isLoading = false;
          },
      });
  }

  openDialog(data?: Income): void {
  this.isLoading = true;

  // Creamos los observables de todas las dependencias
  const users$ = this.userService.getUsers();
  const categories$ = this.incomecategoryService.getAll();
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
      const baseConfig = this.formFactory.getFormConfig('income');

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
          title: data ? 'Edit Income' : 'New Income',
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
    },
    error: (error) => {
      console.error('Error loading related data:', error);
      this.isLoading = false;
    },
  });
}


  edit(income: Income): void {
    this.openDialog(income);
  }

  add(): void {
    this.openDialog();
  }

  update(income: Income): void {
    this.incomeService.update(income.id, income).subscribe({
      next: (response: ApiResponse<Income>) => {
        const updated = response.response;
        const index = this.incomes.findIndex((h) => h.id === updated.id);
        if (index !== -1) {
          this.incomes[index] = updated;
          this.incomes = [...this.incomes];
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
    });
  }

  create(income: Income): void {
    this.incomeService.create(income).subscribe({
      next: (response: ApiResponse<Income>) => {
        this.incomes.push(response.response);
        this.incomes = [...this.incomes];
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
