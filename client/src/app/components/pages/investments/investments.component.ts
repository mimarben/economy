import { Component, ChangeDetectorRef, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { GenericDialogComponent } from '../../shared/generic-dialog/generic-dialog.component';
import {
  GenericTableComponent,
  TableColumn,
} from '../../shared/generic-table/generic-table.component';
import { forkJoin } from 'rxjs';
import { ApiResponse } from '@models/apiResponse';
import { FormFactoryService } from '../../../factories/forms/form-factory.service';
import { FormFieldConfig } from '../../shared/generic-form/form-config';
import { ToastService } from '@services/toast.service';
import { environment } from '../../../../environments/environment';
import { InvestmentBase as Investment } from '@models/InvestmentBase';
import { InvestmentService } from '@services/investment.service';
import { UserService } from '@services/user.service';
import { UtilsService } from '../../../utils/utils.service';
import { UserBase as User } from '@models/UserBase';
import { AccountService } from '@services/account.service';
import { InvestmentCategoryService } from '@services/investment-category.service';
import { AccountBase as Account } from '@models/AccountBase';
import { InvestmentCategoryBase as InvestmentCategory } from '@models/InvestmentCategoryBase';

@Component({
  selector: 'app-investments',
  imports: [GenericTableComponent],
  templateUrl: './investments.component.html',
  styleUrl: './investments.component.css'
})
export class InvestmentsComponent implements OnInit {
investments: Investment[]=[];
filterValue= '';
errorMessage = '';
isLoading= false;
formFields: FormFieldConfig[] = [];
isFormValid= false;
columns: TableColumn<Investment>[]=[];
investmentlogsMap: Record<number, string> = {};
usersMap: Record<number, string> = {};
accountMap: Record<number, string> = {};
categoryMap: Record<number, string> = {};
constructor(
  private investmentService: InvestmentService,
  private userService: UserService,
  private utilsService: UtilsService,
  private cdr: ChangeDetectorRef,
  private dialog: MatDialog,
  private toastService: ToastService,
  private formFactory: FormFactoryService,
  private accountService: AccountService,
  private investmentCategoryService: InvestmentCategoryService
){}

  ngOnInit(): void {
    this.formFields = this.formFactory.getFormConfig('investment');
    this.columns = this.formFactory.getTableColumns<Investment>('investment',
      {user_id:  (value: number) => this.usersMap[value] ?? value,
        account_id: (value: number) => this.accountMap[value] ?? value,
        category_id: (value: number) => this.categoryMap[value] ?? value,
      date: (value: string) => this.utilsService.formatDateLong(value)});
    this.loadInvestments();
  }


  loadInvestments() {
  this.isLoading = true;

  forkJoin({
    investments: this.investmentService.getAll(),
    users: this.userService.getUsers(),
    accounts: this.accountService.getAll(),
    categories: this.investmentCategoryService.getAll()
  }).subscribe({
    next: ({ investments, users, accounts, categories }) => {
      // Comprobar si `.response` existe, si no, fallback al objeto completo
      //this.investments = investments?.response ?? investments ?? [];
      this.investments = investments.response;
      this.usersMap = Object.fromEntries(
        (users?.response ?? users ?? []).map((u: User) => [u.id, `${u.name} ${u.surname1} ${u.surname2}`])
      );
      this.accountMap = Object.fromEntries(
        (accounts?.response ?? accounts ?? []).map((a: Account) => [a.id, `${a.name} ${a.description}`])
      );
      this.categoryMap = Object.fromEntries(
        (categories?.response ?? categories ?? []).map((c: InvestmentCategory) => [c.id, c.name])
      );

      this.isLoading = false;

      // Forzar Angular a actualizar la vista
      this.cdr.detectChanges();

    },
    error: (err) => {
      this.errorMessage = 'Error loading investments';
      this.isLoading = false;
      console.error('Error loading investments data:', err);
    }
  });
}

  editInvestment(investment: Investment): void {
    this.openDialog(investment);
  }
  addInvestment(): void {
    this.openDialog();
  }
  openDialog(data?: Investment): void {
    // Cargar bancos y usuarios en paralelo
    forkJoin({
      users: this.userService.getUsers(),
      accounts: this.accountService.getAll(),
      categories: this.investmentCategoryService.getAll()
    }).subscribe({
      next: (responses) => {
        // Obtener configuración base del formulario
        const baseConfig = this.formFactory.getFormConfig('investment');

        // Enriquecer los campos select con las opciones
        const enrichedConfig = baseConfig.map((field: FormFieldConfig) => {
          if (field.key === 'user_id') {
            return {
              ...field,
              options: responses.users.response.map((r: User) => ({
                value: r.id,
                label: `${r.name} ${r.surname1} ${r.surname2}`
              }))
            };
          }
          if (field.key === 'account_id') {
            return {
              ...field,
              options: responses.accounts.response.map((r: Account) => ({
                value: r.id,
                label: `${r.name}`
              }))
            };
          }
          if (field.key === 'category_id') {
            return {
              ...field,
              options: responses.categories.response.map(r => ({
                value: r.id,
                label: r.name
              }))
            };
          }
          return field;
        });
        const dialogRef = this.dialog.open(GenericDialogComponent, {
          data: {
            title: data ? 'Edit Investment' : 'New Investment',
            fields: enrichedConfig,
            initialData: data || {}
          }
        });

        dialogRef.afterClosed().subscribe(result => {
          if (result) {
            result.id ? this.updateInvestment(result) : this.createInvestment(result);
          }
        });
      },
      error: (error) => {
        console.error('Error loading banks and users:', error);
        // Opcional: Mostrar un snackbar o mensaje de error
      }
    });
  }

  updateInvestment(investment: Investment): void {
    this.investmentService.update(investment.id, investment).subscribe({
      next: (response: ApiResponse<Investment>) => {
        const updated = response.response;
        const index = this.investments.findIndex((h) => h.id === updated.id);
        if (index !== -1) {
          this.investments[index] = updated;
          this.investments = [...this.investments];
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
  createInvestment(investment: Investment): void {
    this.investmentService.create(investment).subscribe({
      next: (response: ApiResponse<Investment>) => {
        this.investments.push(response.response);
        this.investments = [...this.investments];
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
