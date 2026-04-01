import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { GenericDialogComponent } from '@shared/generic-dialog/generic-dialog.component';
import { SourceBase as Source } from '@finance_models/SourceBase';
import { GenericTableComponent, TableColumn } from "@shared/generic-table/generic-table.component";
import { ApiResponse } from '@app/models/core/APIResponse';
import { FormFactoryService } from '@app/core/factories/form-factory.service';
import { FormFieldConfig } from '@shared/generic-form/form-config';
import { ToastService } from '@core_services/toast.service';
import { MetaService } from '@core_services/meta.service';
import { environment } from '@env/environment';
import { SourceService } from '@finance_services/source.service';
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
          private formFactory: FormFactoryService,
          private metaService: MetaService
          ){}
ngOnInit(): void {
  this.metaService.getMeta('source').subscribe(meta => {
    this.formFields = meta.fields;
    this.columns = [
      { key: 'id', label: 'Id', sortable: true }, // opcional pero recomendable
      ...this.formFactory.getTableColumnsFromMetadata(meta.fields)
    ];
    console.log(this.columns);
    this.loadSources();
  });
}
loadSources(){
this.isLoading = true;
    this.sourceService.getAll().subscribe({
      next: (data: ApiResponse<Source[]>) => {
        this.sources = data.response;
        this.isLoading = false;
      },
      error: (err) => {
        this.errorMessage = 'Error loading savings sources';
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
        fields: this.formFields,
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
    this.sourceService.update(source.id!, source).subscribe({
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
