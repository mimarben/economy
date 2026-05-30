import { Component, ChangeDetectorRef, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { forkJoin } from 'rxjs';
import { GenericDialogComponent } from '@shared/generic-dialog/generic-dialog.component';
import { GenericTableComponent, TableColumn } from '@shared/generic-table/generic-table.component';
import { ApiResponse } from '@app/models/core/APIResponse';
import { FormFactoryService } from '@app/core/factories/form-factory.service';
import { FormFieldConfig } from '@shared/generic-form/form-config';
import { ToastService } from '@core_services/toast.service';
import { MetaService } from '@core_services/meta.service';
import { environment } from '@env/environment';
import { InvestmentCategoryBase as InvestmentCategory } from '@investments_models/InvestmentCategoryBase';
import { InvestmentCategoryService } from '@investments_services/investment-category.service';

@Component({
  selector: 'app-investmentsCategories-categories',
  imports: [GenericTableComponent],
  templateUrl: './investments-categories.component.html',
  styleUrl: './investments-categories.component.css'
})
export class InvestmentsCategoriesComponent implements OnInit {
  investmentsCategories: InvestmentCategory[] = [];
  filterValue = '';
  errorMessage = '';
  isLoading = false;
  formFields: FormFieldConfig[] = [];
  columns: TableColumn<InvestmentCategory>[] = [];

  constructor(
    private investmentCategoryService: InvestmentCategoryService,
    private cdr: ChangeDetectorRef,
    private dialog: MatDialog,
    private toastService: ToastService,
    private formFactory: FormFactoryService,
    private metaService: MetaService,
  ) {}

  ngOnInit(): void {
    this.loadInitialData();
  }

  private loadInitialData(): void {
    this.isLoading = true;
    forkJoin({
      categories: this.investmentCategoryService.getAll(),
      meta: this.metaService.getMeta('investment-category'),
    }).subscribe({
      next: ({ categories, meta }) => {
        this.investmentsCategories = categories.response;
        this.formFields = this.formFactory.enrichMetadataFields(meta.fields);
        this.columns = this.formFactory.getTableColumnsFromMetadata<InvestmentCategory>(this.formFields);
        this.isLoading = false;
        this.cdr.detectChanges();
      },
      error: () => {
        this.errorMessage = 'Error loading investment categories';
        this.isLoading = false;
      },
    });
  }

  editInvestmentCategory(investmentCategory: InvestmentCategory): void {
    this.openDialog(investmentCategory);
  }

  addInvestmentInvestmentCategory(): void {
    this.openDialog();
  }

  openDialog(data?: InvestmentCategory): void {
    const dialogRef = this.dialog.open(GenericDialogComponent, {
      data: {
        title: data ? 'Edit Investment Category' : 'New Investment Category',
        fields: this.formFields,
        initialData: data || {},
      },
    });

    dialogRef.afterClosed().subscribe((result) => {
      if (result) {
        result.id ? this.updateInvestmentCategory(result) : this.createInvestmentCategory(result);
      }
    });
  }

  updateInvestmentCategory(investmentCategory: InvestmentCategory): void {
    this.investmentCategoryService.update(investmentCategory.id!, investmentCategory).subscribe({
      next: (response: ApiResponse<InvestmentCategory>) => {
        const updated = response.response;
        const index = this.investmentsCategories.findIndex((h) => h.id === updated.id);
        if (index !== -1) {
          this.investmentsCategories[index] = updated;
          this.investmentsCategories = [...this.investmentsCategories];
        }
        this.toastService.showToast(response, environment.toastType.Success, {});
        this.cdr.detectChanges();
      },
      error: (err) => {
        this.toastService.showToast(err.error as ApiResponse<string>, environment.toastType.Error, {});
      },
    });
  }

  createInvestmentCategory(investmentCategory: InvestmentCategory): void {
    this.investmentCategoryService.create(investmentCategory).subscribe({
      next: (response: ApiResponse<InvestmentCategory>) => {
        this.investmentsCategories.push(response.response);
        this.investmentsCategories = [...this.investmentsCategories];
        this.toastService.showToast(response, environment.toastType.Success, {});
        this.cdr.detectChanges();
      },
      error: (err) => {
        this.toastService.showToast(err.error as ApiResponse<string>, environment.toastType.Error, {});
      },
    });
  }

  applyFilter(event: Event) {
    this.filterValue = (event.target as HTMLInputElement).value.trim().toLowerCase();
  }
}
