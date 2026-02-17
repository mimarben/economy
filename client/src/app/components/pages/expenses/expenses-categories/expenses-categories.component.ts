import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { GenericTableComponent, TableColumn } from '@shared/generic-table/generic-table.component';
import { GenericDialogComponent } from '@shared/generic-dialog/generic-dialog.component';
import { ToastService } from '@core_services/toast.service';
import { environment } from '@environments/environment';
import { ApiResponse } from '@core_models/apiResponse';
import { FormFieldConfig } from '@shared/generic-form/form-config';
import { FormFactoryService } from '@factories/forms/form-factory.service';
import { ExpenseCategoryBase as ExpenseCategory } from '@expenses_models/ExpenseCategoryBase';
import { ExpenseCategoryService } from '@app/services/expenses/expense-category.service';
import { CommonModule } from '@angular/common'; // Asegúrate de tener CommonModule si usas Directivas

@Component({
  selector: 'app-expenses-categories',
  // Es importante usar 'CommonModule' y 'GenericTableComponent' aquí.
  // Tu código original solo tenía GenericTableComponent, si es un componente standalone.
  imports: [GenericTableComponent, CommonModule],
  templateUrl: './expenses-categories.component.html',
  styleUrl: './expenses-categories.component.css',
})
export class ExpensesCategoriesComponent implements OnInit {
  expensesCategories: ExpenseCategory[] = [];
  filterValue = '';
  isLoading = false;
  errorMessage = '';
  formFields: FormFieldConfig[] = [];
  columns: TableColumn<any>[] = [];
  isFormValid = false;
  expensesCategoriesMap: Record<number, string> = {}; // Inicializar como objeto vacío

  ngOnInit(): void {
    // Nota: Es inusual obtener 'saving_log' aquí, pero mantengo tu código.
    this.formFields = this.formFactory.getFormConfig('saving_log');
    this.columns = this.formFactory.getTableColumns<ExpenseCategory>('expense_category');
    this.loadExpensesCategories();
  }

  constructor(
    private cdr: ChangeDetectorRef,
    private dialog: MatDialog,
    private toastService: ToastService,
    private formFactory: FormFactoryService,
    private expenseCategoryService: ExpenseCategoryService // Servicio de Gastos
  ) {}

  /**
   * Carga la lista de categorías de gastos desde el servicio.
   */
  loadExpensesCategories() {
    this.isLoading = true;
        this.expenseCategoryService.getAll().subscribe({
          next: (data: ApiResponse<ExpenseCategory[]>) => {
            this.expensesCategories = data.response;
            this.isLoading = false;
          },
          error: (err) => {
            this.errorMessage = 'Error loading accounts';
            this.isLoading = false;
          },
        });
        console.log("Categories: ", this.expensesCategories);
  }

  // ... el resto de tus métodos (edit, add, openDialog, update, create, applyFilter) ...

    edit(expensecategory: ExpenseCategory): void {
      this.openDialog(expensecategory);
    }

    add(): void {
      this.openDialog();
    }

    openDialog(data?: ExpenseCategory): void {
      const dialogRef = this.dialog.open(GenericDialogComponent, {
        data: {
          // Nota: Corregí el título de 'Edit Icome Category' a 'Edit Expense Category'
          title: data ? 'Edit Expense Category' : 'New Expense Category',
          fields: this.formFactory.getFormConfig('expense_category'),
          initialData: data || {},
        },
      });

      dialogRef.afterClosed().subscribe((result) => {
        if (result) {
          result.id ? this.update(result) : this.create(result);
        }
      });
    }

    // ... (Los métodos update, create, applyFilter se mantienen sin cambios) ...

    update(expensecategory: ExpenseCategory): void {
          this.expenseCategoryService.update(expensecategory.id, expensecategory).subscribe({
            next: (response: ApiResponse<ExpenseCategory>) => {
              this.isLoading = false;
              this.toastService.showToast(
                response,
                environment.toastType.Success,
                {}
              );
              const updateIExpenseCategory = response.response;
              const index = this.expensesCategories.findIndex((r) => r.id === updateIExpenseCategory.id);
              if (index !== -1) {
                this.expensesCategories[index] = updateIExpenseCategory;
                this.expensesCategories = [...this.expensesCategories]; // Reassign to trigger change detection
              }
              this.cdr.detectChanges();
            },
            error: (error) => {
              console.error('Error updating expense categories:', error.error);
              this.isLoading = false;
              this.toastService.showToast(
                error.error as ApiResponse<string>,
                environment.toastType.Error,
                {}
              );
            },
          });
        }
    create(expensecategory: ExpenseCategory): void {
      this.expenseCategoryService.create(expensecategory).subscribe({
        next: (response: ApiResponse<ExpenseCategory>) => {
          this.isLoading = false;
          this.toastService.showToast(
            response,
            environment.toastType.Success,
            {}
          );
          const newExpenseCategory = response.response;
          this.expensesCategories.push(newExpenseCategory); // Add the new bank to the array
          this.expensesCategories = [...this.expensesCategories]; // Reassign to trigger change detection
          this.cdr.detectChanges();
        },
        error: (error) => {
          console.error('Error creating expense category:', error.error);
          this.isLoading = false;
          this.errorMessage = 'Failed to create expense category.';
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
