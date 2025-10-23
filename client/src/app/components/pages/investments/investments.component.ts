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
import { InvestmentBase as Investment } from '../../../models/InvestmentBase';
import { InvestmentService } from '../../../services/investment.service';
import { UserService } from '../../../services/user.service';
import { UtilsService } from '../../../utils/utils.service';
import { UserBase as User } from '../../../models/UserBase';

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
usersMap: Record<number, string> = {};
constructor(
  private investmentService: InvestmentService,
  private userService: UserService,
  private utilsService: UtilsService,
  private cdr: ChangeDetectorRef,
  private dialog: MatDialog,
  private toastService: ToastService,
  private formFactory: FormFactoryService
){}

  ngOnInit(): void {
    this.formFields = this.formFactory.getFormConfig('investment');
    this.columns = this.formFactory.getTableColumns<Investment>('investment',
      {user_id:  (value: number) => this.usersMap[value] ?? value,
      date: (value: string) => this.utilsService.moment(value).format('YYYY-MM-DD HH:MM')});
    this.loadInvestments();
  }

  loadInvestments() {
      this.isLoading = true;
      this.investmentService.getAll().subscribe({
        next: (data: ApiResponse<Investment[]>) => {
          this.investments = data.response;
          this.isLoading = false;
        },
        error: (err) => {
          this.errorMessage = 'Error loading investments';
          this.isLoading = false;
        },
      });
      this.userService.getUsers().subscribe({
        next: (res: ApiResponse<User[]>) => {
          const userField = this.formFields.find(f => f.key === 'user_id');
          if (userField) {
            this.usersMap = Object.fromEntries(res.response.map(u=>[u.id, (`${u.name} ${u.surname1} ${u.surname2}`)]))
          }
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
      const dialogRef = this.dialog.open(GenericDialogComponent, {
        data: {
          title: data ? 'Edit Investment' : 'New Investment',
          fields: this.formFactory.getFormConfig('investment'),
          initialData: data || {},
        },
      });

      dialogRef.afterClosed().subscribe((result) => {
        if (result) {
          result.id ? this.updateInvestment(result) : this.createInvestment(result);
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
