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
import { SavingService } from '../../../services/saving.service';
import { UserService } from '../../../services/user.service';
import { UtilsService } from '../../../utils/utils.service';

@Component({
  selector: 'app-savings',
  imports: [GenericTableComponent],
  templateUrl: './savings.component.html',
  styleUrl: './savings.component.css',
})
export class SavingsComponent implements OnInit{
  savings: Saving[] = [];
  filterValue = '';
  isLoading = false;
  errorMessage = '';
  formFields: FormFieldConfig[] = [];
  isFormValid = false;
  columns: TableColumn<Saving>[] = [];
  usersMap: Record<number, string> = {};
  constructor(
    private savingService: SavingService,
    private userService: UserService,
    private utilsService:UtilsService,
    private cdr: ChangeDetectorRef,
    private dialog: MatDialog,
    private toastService: ToastService,
    private formFactory: FormFactoryService
  ) {}

  ngOnInit(): void {
    this.formFields = this.formFactory.getFormConfig('saving');
    this.columns = this.formFactory.getTableColumns<Saving>('saving',
      {user_id:  (value: number) => this.usersMap[value] ?? value,
      date: (value: string) => this.utilsService.moment(value).format('YYYY-MM-DD HH:MM')});
    this.loadSavings();
  }
  loadSavings() {
    this.isLoading = true;
    this.savingService.getAll().subscribe({
      next: (data: ApiResponse<Saving[]>) => {
        this.savings = data.response;
        this.isLoading = false;
      },
      error: (err) => {
        this.errorMessage = 'Error loading banks';
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

  editSaving(savinglog: Saving): void {
    this.openDialog(savinglog);
  }
  addSaving(): void {
    this.openDialog();
  }
  openDialog(data?: Saving): void {
    const dialogRef = this.dialog.open(GenericDialogComponent, {
      data: {
        title: data ? 'Edit Saving' : 'New Saving',
        fields: this.formFactory.getFormConfig('saving_log'),
        initialData: data || {},
      },
    });

    dialogRef.afterClosed().subscribe((result) => {
      if (result) {
        result.id ? this.updateSaving(result) : this.createSaving(result);
      }
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
