import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { GenericDialogComponent } from '../../shared/generic-dialog/generic-dialog.component';
import { HouseholdBase as Household } from '../../../models/HouseholdBase';
import { GenericTableComponent, TableColumn } from "../../shared/generic-table/generic-table.component";
import { ApiResponse } from '../../../models/apiResponse';
import { FormFactoryService } from '../../../factories/forms/form-factory.service';
import { FormFieldConfig } from '../../shared/generic-form/form-config';
import { ToastService } from '../../../services/toast.service';
import { environment } from '../../../../environments/environment';
import { HouseholdService } from '../../../services/household.service';

@Component({
  selector: 'app-households',
  imports: [GenericTableComponent],
  templateUrl: './households.component.html',
  styleUrl: './households.component.css'
})
export class HouseholdsComponent implements OnInit{
houseHolds: Household[]=[]
filterValue=''
isLoading= false
errorMessage=''
formFields: FormFieldConfig[]=[]
isFormValid= false
columns: TableColumn<Household>[]=[]

constructor(
          private householdService: HouseholdService,
          private cdr: ChangeDetectorRef,
          private dialog: MatDialog,
          private toastService: ToastService,
          private formFactory: FormFactoryService
          ){}
  ngOnInit(): void {
    this.formFields = this.formFactory.getFormConfig('houseHold');
    this.columns = this.formFactory.getTableColumns<Household>('houseHold');
    this.loadHouseHolds();
  }
  loadHouseHolds(){
    this.isLoading = true;
    this.householdService.getAll().subscribe({
      next: (data: ApiResponse<Household[]>) => {
        this.houseHolds = data.response;
        this.isLoading = false;
      },
      error: (err) => {
        this.errorMessage = 'Error loading banks';
        this.isLoading = false;
      },
    });
  }
  editHouseHold(houseHold: Household): void{
    this.openDialog(houseHold)
  }
  addHouseHold():void {
    this.openDialog();
  }
  openDialog(data?: Household): void {
    const dialogRef = this.dialog.open(GenericDialogComponent, {
      data: {
        title: data ? 'Edit HouseHold' : 'New HouseHold',
        fields: this.formFactory.getFormConfig('houseHold'),
        initialData: data || {},
      },
    });

    dialogRef.afterClosed().subscribe((result) => {
      if (result) {
        result.id ? this.updateHouseHold(result) : this.createHouseHold(result);
      }
    });
  }
  updateHouseHold(houseHold: Household): void {
    this.householdService.update(houseHold.id, houseHold).subscribe({
    next: (response: ApiResponse<Household>) => {
      const updated = response.response;
      const index = this.houseHolds.findIndex(h => h.id === updated.id);
      if (index !== -1) {
        this.houseHolds[index] = updated;
        this.houseHolds = [...this.houseHolds];
      }
      this.toastService.showToast(response, environment.toastType.Success, {});
      this.cdr.detectChanges();
    },
    error: (err) => {
      this.toastService.showToast(err.error as ApiResponse<string>, environment.toastType.Error, {});
    }
  });
  }
  createHouseHold(houseHold: Household): void {
    this.householdService.create(houseHold).subscribe({
    next: (response: ApiResponse<Household>) => {
      this.houseHolds.push(response.response);
      this.houseHolds = [...this.houseHolds];
      this.toastService.showToast(response, environment.toastType.Success, {});
      this.cdr.detectChanges();
    },
    error: (err) => {
      this.toastService.showToast(err.error as ApiResponse<string>, environment.toastType.Error, {});
    }
  });
  }

  applyFilter(event: Event) {
    this.filterValue = (event.target as HTMLInputElement).value
      .trim()
      .toLowerCase();
  }
}
