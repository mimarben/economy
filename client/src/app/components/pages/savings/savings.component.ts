import { Component, ChangeDetectorRef, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { GenericDialogComponent } from '../../shared/generic-dialog/generic-dialog.component';
import {
  GenericTableComponent,
  TableColumn,
} from '../../shared/generic-table/generic-table.component';
import { ApiResponse } from '../../../models/apiResponse';
import { FormFactoryService } from '../../../factories/forms/form-factory.service';
import { FormFieldConfig } from '../../shared/generic-form/form-config';
import { ToastService } from '../../../services/toast.service';
import { environment } from '../../../../environments/environment';
import { SavingBase as Saving } from '../../../models/SavingBase';
import { UserBase as User } from '../../../models/UserBase';
import { AccountBase as Account } from '@models/AccountBase';
import { SavingService } from '../../../services/saving.service';
import { UserService } from '../../../services/user.service';
import { UtilsService } from '../../../utils/utils.service';
import { AccountService } from '../../../services/account.service';
import { forkJoin } from 'rxjs';
@Component({
  selector: 'app-savings',
  imports: [GenericTableComponent],
  templateUrl: './savings.component.html',
  styleUrl: './savings.component.css',
})
export class SavingsComponent implements OnInit {
  savings: Saving[] = [];
  filterValue = '';
  isLoading = false;
  errorMessage = '';
  formFields: FormFieldConfig[] = [];
  isFormValid = false;
  columns: TableColumn<Saving>[] = [];
  usersMap: Record<number, string> = {};
  accountsMap: Record<number, string> = {};

  constructor(
    private savingService: SavingService,
    private userService: UserService,
    private utilsService: UtilsService,
    private cdr: ChangeDetectorRef,
    private dialog: MatDialog,
    private toastService: ToastService,
    private formFactory: FormFactoryService,
    private accountService: AccountService
  ) {}

  ngOnInit(): void {
    this.formFields = this.formFactory.getFormConfig('saving');
    this.columns = this.formFactory.getTableColumns<Saving>('saving', {
      user_id: (value: number) => this.usersMap[value] ?? value,
      account_id: (value: number) => this.accountsMap[value] ?? value,
      date: (value: string) => this.utilsService.formatDateLong(value),
    });
    this.loadSavings();
  }
 // Dentro de tu componente
loadSavings() {
    this.isLoading = true;
    this.errorMessage = ''; // Limpiar el error anterior

    const savings$ = this.savingService.getAll();
    const users$ = this.userService.getUsers();
    const accounts$ = this.accountService.getAll();

    // 1. Usar forkJoin para esperar las tres llamadas simultáneamente
    forkJoin([savings$, users$, accounts$]).subscribe({
        next: ([savingsResponse, usersResponse, accountsResponse]) => {
            // 2. Éxito: Los datos están disponibles en el orden del array

            // a) Asignar Ahorros (Savings)
            this.savings = savingsResponse.response || [];

            // b) Mapear Usuarios
            const users = usersResponse.response || [];
            this.usersMap = Object.fromEntries(
                users.map((u) => [
                    u.id,
                    `${u.name} ${u.surname1} ${u.surname2 || ''}`, // Asegurar que surname2 es opcional
                ])
            );

            // c) Mapear Cuentas (Accounts)
            const accounts = accountsResponse.response || [];
            this.accountsMap = Object.fromEntries(
                accounts.map((a) => [a.id, `${a.name}`])
            );

            // 3. Finalizar la carga y forzar la detección de cambios
            this.isLoading = false;
            // Si usas ChangeDetectionStrategy.OnPush, necesitarás esto:
            // this.cdr.detectChanges();
        },
        error: (err) => {
            // 4. Error: Manejar cualquier fallo de las tres llamadas
            console.error('Error al cargar datos:', err);
            this.errorMessage = 'Error loading savings, users, or accounts data.';
            this.isLoading = false;
            // this.cdr.detectChanges();
        },
    });
}
  editSaving(savinglog: Saving): void {
    this.openDialog(savinglog);
  }
  addSaving(): void {
    this.openDialog();
  }
  /*   openDialog(data?: Saving): void {
    const dialogRef = this.dialog.open(GenericDialogComponent, {
      data: {
        title: data ? 'Edit Saving' : 'New Saving',
        fields: this.formFactory.getFormConfig('saving'),
        initialData: data || {},
      },
    });

    dialogRef.afterClosed().subscribe((result) => {
      if (result) {
        result.id ? this.updateSaving(result) : this.createSaving(result);
      }
    });
  } */
  openDialog(data?: Saving): void {
    // Cargar bancos y usuarios en paralelo
    forkJoin({
      users: this.userService.getUsers(),
      accounts: this.accountService.getAll(),
    }).subscribe({
      next: (responses) => {
        // Obtener configuración base del formulario
        const baseConfig = this.formFactory.getFormConfig('saving');

        // Enriquecer los campos select con las opciones
        const enrichedConfig = baseConfig.map((field) => {
          if (field.key === 'user_id') {
            return {
              ...field,
              options: responses.users.response.map((user) => ({
                value: user.id,
                label: user.name,
              })),
            };
          }

          if (field.key === 'account_id') {
            return {
              ...field,
              options: responses.accounts.response.map((account) => ({
                value: account.id,
                label: `${account.name}`,
              })),
            };
          }
          return field;
        });
        const dialogRef = this.dialog.open(GenericDialogComponent, {
          data: {
            title: data ? 'Edit Saving' : 'New Saving',
            fields: enrichedConfig,
            initialData: data || {},
          },
        });

        dialogRef.afterClosed().subscribe((result) => {
          if (result) {
            result.id ? this.updateSaving(result) : this.createSaving(result);
          }
        });
      },
      error: (error) => {
        console.error('Error loading accounts and users:', error);
        // Opcional: Mostrar un snackbar o mensaje de error
      },
    });
  }
  updateSaving(saving: Saving): void {
    this.savingService.update(saving.id, saving).subscribe({
      next: (response: ApiResponse<Saving>) => {
        const updated = response.response;
        const index = this.savings.findIndex((h) => h.id === updated.id);
        if (index !== -1) {
          this.savings[index] = updated;
          this.savings = [...this.savings];
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
  createSaving(saving: Saving): void {
    this.savingService.create(saving).subscribe({
      next: (response: ApiResponse<Saving>) => {
        this.savings.push(response.response);
        this.savings = [...this.savings];
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
