import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { GenericDialogComponent } from '../../shared/generic-dialog/generic-dialog.component';
import { GenericTableComponent, TableColumn } from "../../shared/generic-table/generic-table.component";
import { ApiResponse } from '../../../models/apiResponse';
import { FormFactoryService } from '../../../factories/forms/form-factory.service';
import { FormFieldConfig } from '../../shared/generic-form/form-config';
import { ToastService } from '../../../services/toast.service';
import { environment } from '../../../../environments/environment';
import { SourceBase as Source } from '../../../models/SourceBase';
import { SourceService } from '../../../services/source.service';
@Component({
  selector: 'app-savings',
  imports: [GenericTableComponent],
  templateUrl: './savings.component.html',
  styleUrl: './savings.component.css'
})
export class SavingsComponent {
houseHolds: Source[]=[]
filterValue=''
isLoading= false
errorMessage=''
formFields: FormFieldConfig[]=[]
isFormValid= false
columns: TableColumn<Source>[]=[]

constructor(
          private sourceService: SourceService,
          private cdr: ChangeDetectorRef,
          private dialog: MatDialog,
          private toastService: ToastService,
          private formFactory: FormFactoryService
          ){}

ngOnInit(): void {
    this.formFields = this.formFactory.getFormConfig('source');
    this.columns = this.formFactory.getTableColumns<Source>('source');
    this.loadSource();
  }
loadSource(){}
}
