import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { ImportOriginBase as ImportOrigin } from '@app/models/import/import-originBase';
import { GenericTableComponent, TableColumn } from '@shared/generic-table/generic-table.component';
import { ApiResponse } from '@app/models/core/APIResponse';
import { GenericDialogComponent } from '@shared/generic-dialog/generic-dialog.component';
import { FormFactoryService } from '@app/core/factories/form-factory.service';
import { ImportOriginsService, ImportOriginCreate } from '@import_services/import-profiles.service';
import { FormFieldConfig } from '@shared/generic-form/form-config';
import { ToastService } from '@core_services/toast.service';
import { environment } from '@env/environment';
import { MetaService } from '@core_services/meta.service';
import { forkJoin } from 'rxjs';

@Component({
  selector: 'app-import-origins',
  imports: [GenericTableComponent],
  templateUrl: './import-origins.component.html',
  styleUrls: ['./import-origins.component.scss'],
})
export class ImportOriginsComponent implements OnInit {
  origins: ImportOrigin[] = [];
  filterValue = '';
  isLoading = false;
  errorMessage = '';
  formFields: FormFieldConfig[] = [];
  isFormValid = false;

  columns: TableColumn<ImportOrigin>[] = [
    { key: 'id', label: 'ID', sortable: true },
    { key: 'code', label: 'Code', sortable: true },
    { key: 'name', label: 'Name', sortable: true },
    { key: 'active', label: 'Active', sortable: true, formatter: (v) => (v ? 'Yes' : 'No') },
  ];

  constructor(
    private importOriginsService: ImportOriginsService,
    private cdr: ChangeDetectorRef,
    private dialog: MatDialog,
    private toastService: ToastService,
    private formFactory: FormFactoryService,
    private metaService: MetaService,
  ) {}

  ngOnInit() {
    this.loadInitialData();
  }

  loadInitialData() {
    this.isLoading = true;
    forkJoin({
      origins: this.importOriginsService.getOrigins(),
      meta: this.metaService.getMeta('import-origins'),
    }).subscribe({
      next: ({ origins, meta }) => {
        this.origins = origins.response;
        this.formFields = meta.fields;

        this.columns = this.formFactory.getTableColumnsFromMetadata<ImportOrigin>(
          this.formFields,
        );

        this.isLoading = false;
      },
      error: (err: any) => {
        this.errorMessage = 'Error loading data';
        this.isLoading = false;
      },
    });
  }

  editOrigin(origin: ImportOrigin): void {
    this.openDialog(origin);
  }

  addOrigin(): void {
    this.openDialog();
  }

  openDialog(data?: ImportOrigin): void {
    const dialogRef = this.dialog.open(GenericDialogComponent, {
      data: {
        title: data ? 'Edit Origin' : 'New Origin',
        fields: this.formFields,
        initialData: data || {},
      },
    });

    dialogRef.afterClosed().subscribe((result) => {
      if (result) {
        result.id ? this.updateOrigin(result) : this.createOrigin(result);
      }
    });
  }

  createOrigin(origin: ImportOriginCreate): void {
    this.importOriginsService.createOrigin(origin).subscribe({
      next: (response) => {
        this.toastService.showToast(response, environment.toastType.Success);
        this.loadInitialData();
      },
      error: (error) => {
        this.toastService.showToast(error.error as ApiResponse<string>, environment.toastType.Error);
      }
    });
  }

  updateOrigin(origin: ImportOrigin): void {
    this.importOriginsService.updateOrigin(origin.id, origin).subscribe({
      next: (response) => {
        this.toastService.showToast(response, environment.toastType.Success);
        this.loadInitialData();
      },
      error: (error) => {
        this.toastService.showToast(error.error as ApiResponse<string>, environment.toastType.Error);
      }
    });
  }

  deleteOrigin(origin: ImportOrigin): void {
    if (confirm('Are you sure you want to delete this origin?')) {
      this.importOriginsService.deleteOrigin(origin.id).subscribe({
        next: (response) => {
          this.toastService.showToast(response, environment.toastType.Success);
          this.loadInitialData();
        },
        error: (error) => {
          this.toastService.showToast(error.error as ApiResponse<string>, environment.toastType.Error);
        }
      });
    }
  }
}