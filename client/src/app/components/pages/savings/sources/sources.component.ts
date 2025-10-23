import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { GenericDialogComponent } from '../../../shared/generic-dialog/generic-dialog.component';
import { SourceBase as Source } from '../../../../models/SourceBase';
import { GenericTableComponent, TableColumn } from "../../../shared/generic-table/generic-table.component";
import { ApiResponse } from '../../../../models/apiResponse';
import { FormFactoryService } from '../../../../factories/forms/form-factory.service';
import { FormFieldConfig } from '../../../shared/generic-form/form-config';
import { ToastService } from '../../../../services/toast.service';
import { environment } from '../../../../../environments/environment';
import { SourceService } from '../../../../services/source.service';
@Component({
  selector: 'app-sources',
  imports: [GenericTableComponent],
  templateUrl: './sources.component.html',
  styleUrl: './sources.component.css'
})
export class SourcesComponent implements OnInit{
sources: Source[]=[]
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
    this.loadSources();
  }
loadSources(){
this.isLoading = true;
    this.sourceService.getAll().subscribe({
      next: (data: ApiResponse<Source[]>) => {
        this.sources = data.response;
        this.isLoading = false;
      },
      error: (err) => {
        this.errorMessage = 'Error loading banks';
        this.isLoading = false;
      },
    });
}
editSource(source: Source): void{
    this.openDialog(source)
  }
addSource():void {
  this.openDialog();
  }
openDialog(data?: Source): void {
    const dialogRef = this.dialog.open(GenericDialogComponent, {
      data: {
        title: data ? 'Edit Source' : 'New Source',
        fields: this.formFactory.getFormConfig('source'),
        initialData: data || {},
      },
    });
    dialogRef.afterClosed().subscribe((result) => {
      console.log(result);
      if (result) {
        result.id ? this.updateSource(result) : this.createSource(result);
      }
    });
  }
  updateSource(source: Source): void {
    this.sourceService.update(source.id, source).subscribe({
    next: (response: ApiResponse<Source>) => {
      const updated = response.response;
      const index = this.sources.findIndex(h => h.id === updated.id);
      if (index !== -1) {
        this.sources[index] = updated;
        this.sources = [...this.sources];
      }
      this.toastService.showToast(response, environment.toastType.Success, {});
      this.cdr.detectChanges();
    },
    error: (err) => {
      this.toastService.showToast(err.error as ApiResponse<string>, environment.toastType.Error, {});
    }
  });
  }
  createSource(source: Source): void {
    this.sourceService.create(source).subscribe({
    next: (response: ApiResponse<Source>) => {
      this.sources.push(response.response);
      this.sources = [...this.sources];
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
