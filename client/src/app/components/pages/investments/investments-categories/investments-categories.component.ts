import { Component, ChangeDetectorRef, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { GenericDialogComponent } from '../../../shared/generic-dialog/generic-dialog.component';
import {
  GenericTableComponent,
  TableColumn,
} from '../../../shared/generic-table/generic-table.component';
import { ApiResponse } from '../../../../models/apiResponse';
import { FormFactoryService } from '../../../../factories/forms/form-factory.service';
import { FormFieldConfig } from '../../../shared/generic-form/form-config';
import { ToastService } from '../../../../services/toast.service';
import { environment } from '../../../../../environments/environment';
import { InvestmentCategoryBase as InvestmentCategory } from '../../../../models/InvestmentCategoryBase';
import { InvestmentCategoryService } from '../../../../services/investment-category.service';
import { UserService } from '../../../../services/user.service';
import { UtilsService } from '../../../../utils/utils.service';
import { UserBase as User } from '../../../../models/UserBase';

@Component({
  selector: 'app-investmentsCategories-categories',
  imports: [GenericTableComponent],
  templateUrl: './investments-categories.component.html',
  styleUrl: './investments-categories.component.css'
})
export class InvestmentsCategoriesComponent implements OnInit {
investmentsCategories: InvestmentCategory[]=[];
filterValue= '';
errorMessage = '';
isLoading= false;
formFields: FormFieldConfig[] = [];
isFormValid= false;
columns: TableColumn<InvestmentCategory>[]=[];
usersMap: Record<number, string> = {};
constructor(
  private investmentCategoryService: InvestmentCategoryService,
  private userService: UserService,
  private utilsService: UtilsService,
  private cdr: ChangeDetectorRef,
  private dialog: MatDialog,
  private toastService: ToastService,
  private formFactory: FormFactoryService
){}

  ngOnInit(): void {
    this.formFields = this.formFactory.getFormConfig('investment_category');
    this.columns = this.formFactory.getTableColumns<InvestmentCategory>('investment_category',
      {user_id:  (value: number) => this.usersMap[value] ?? value,
      date: (value: string) => this.utilsService.formatDateLong(value)});
    this.loadInvestments();
  }

  loadInvestments() {
      this.isLoading = true;
      this.investmentCategoryService.getAll().subscribe({
        next: (data: ApiResponse<InvestmentCategory[]>) => {
          this.investmentsCategories = data.response;
          this.isLoading = false;
        },
        error: (err: any) => {
          this.errorMessage = 'Error loading investments Categories';
          this.isLoading = false;
        },
      });
      this.userService.getUsers().subscribe({
        next: (res: ApiResponse<User[]>) => {
          const userField = this.formFields.find(f => f.key === 'user_id');
          if (userField) {
            this.usersMap = Object.fromEntries(res.response.map((u: User)=>[u.id, (`${u.name} ${u.surname1} ${u.surname2}`)]))
          }
        }
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
          fields: this.formFactory.getFormConfig('investment_category'),
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
    this.investmentCategoryService.update(investmentCategory.id, investmentCategory).subscribe({
      next: (response: ApiResponse<InvestmentCategory>) => {
        const updated = response.response;
        const index = this.investmentsCategories.findIndex((h) => h.id === updated.id);
        if (index !== -1) {
          this.investmentsCategories[index] = updated;
          this.investmentsCategories = [...this.investmentsCategories];
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
  createInvestmentCategory(investmentCategory: InvestmentCategory): void {
    this.investmentCategoryService.create(investmentCategory).subscribe({
      next: (response: ApiResponse<InvestmentCategory>) => {
        this.investmentsCategories.push(response.response);
        this.investmentsCategories = [...this.investmentsCategories];
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
