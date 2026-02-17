import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { GenericTableComponent, TableColumn } from '@shared/generic-table/generic-table.component';
import { GenericDialogComponent } from '@shared/generic-dialog/generic-dialog.component';
import { ToastService } from '@core_services/toast.service';
import { environment } from '@environments/environment';
import { ApiResponse } from '@core_models/apiResponse';
import { FormFieldConfig } from '@shared/generic-form/form-config';
import { FormFactoryService } from '@factories/forms/form-factory.service';
import { IncomeCategoryBase as IncomeCategory } from '@incomes_models/IncomeCategoryBase';
import { IncomeCategoryService } from '@incomes_services/income-category.service';
@Component({
  selector: 'app-incomes-categories',
  imports: [GenericTableComponent],
  templateUrl: './incomes-categories.component.html',
  styleUrl: './incomes-categories.component.css',
})
export class IncomesCategoriesComponent implements OnInit {
  incomesCategories: IncomeCategory[] = [];
  filterValue = '';
  isLoading = false;
  errorMessage = '';
  formFields: FormFieldConfig[] = [];
  columns: TableColumn<any>[] = [];
  isFormValid = false;
  incomesCategoriesMap: Record<number, string> = [];
  ngOnInit(): void {
    this.formFields = this.formFactory.getFormConfig('saving_log');
    this.columns = this.formFactory.getTableColumns<IncomeCategory>('income_category');
    this.loadIncomesCategories();
  }
  constructor(
    private cdr: ChangeDetectorRef,
    private dialog: MatDialog,
    private toastService: ToastService,
    private formFactory: FormFactoryService,
    private incomeCategoryService: IncomeCategoryService
  ) {}

  loadIncomesCategories() {
    this.isLoading = true;
    this.incomeCategoryService.getAll().subscribe({
      next: (data: ApiResponse<IncomeCategory[]>) => {
        this.incomesCategories = data.response;
        this.isLoading = false;
      },
      error: (err) => {
        this.errorMessage = 'Error loading accounts';
        this.isLoading = false;
      },
    });
  }
    edit(incomecategory: IncomeCategory): void {
      this.openDialog(incomecategory);
    }

    add(): void {
      this.openDialog();
    }
  openDialog(data?: IncomeCategory): void {
      const dialogRef = this.dialog.open(GenericDialogComponent, {
        data: {
          title: data ? 'Edit Icome Category' : 'New Income Category',
          fields: this.formFactory.getFormConfig('income_category'),
          initialData: data || {},
        },
      });

      dialogRef.afterClosed().subscribe((result) => {
        if (result) {
          result.id ? this.update(result) : this.create(result);
        }
      });
    }

    update(incomecategory: IncomeCategory): void {
      this.incomeCategoryService.update(incomecategory.id, incomecategory).subscribe({
        next: (response: ApiResponse<IncomeCategory>) => {
          this.isLoading = false;
          this.toastService.showToast(
            response,
            environment.toastType.Success,
            {}
          );
          const updateIncomeCategory = response.response;
          const index = this.incomesCategories.findIndex((r) => r.id === updateIncomeCategory.id);
          if (index !== -1) {
            this.incomesCategories[index] = updateIncomeCategory;
            this.incomesCategories = [...this.incomesCategories]; // Reassign to trigger change detection
          }
          this.cdr.detectChanges();
        },
        error: (error) => {
          console.error('Error updating income categories:', error.error);
          this.isLoading = false;
          this.toastService.showToast(
            error.error as ApiResponse<string>,
            environment.toastType.Error,
            {}
          );
        },
      });
    }

    create(incomecategory: IncomeCategory): void {
      this.incomeCategoryService.create(incomecategory).subscribe({
        next: (response: ApiResponse<IncomeCategory>) => {
          this.isLoading = false;
          this.toastService.showToast(
            response,
            environment.toastType.Success,
            {}
          );
          const newIncomeCategory = response.response;
          this.incomesCategories.push(newIncomeCategory); // Add the new bank to the array
          this.incomesCategories = [...this.incomesCategories]; // Reassign to trigger change detection
          this.cdr.detectChanges();
        },
        error: (error) => {
          console.error('Error creating income category:', error.error);
          this.isLoading = false;
          this.errorMessage = 'Failed to create income category.';
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
