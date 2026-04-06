import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { ImportProfileBase as ImportProfile } from '@app/models/import/import-profileBase';
import { ImportOriginBase as ImportOrigin } from '@app/models/import/import-originBase';
import { GenericTableComponent, TableColumn } from '@shared/generic-table/generic-table.component';
import { ApiResponse } from '@app/models/core/APIResponse';
import { GenericDialogComponent } from '@shared/generic-dialog/generic-dialog.component';
import { FormFactoryService } from '@app/core/factories/form-factory.service';
import { ImportProfilesService, ImportOriginsService, ImportProfileCreate } from '@import_services/import-profiles.service';
import { FormFieldConfig } from '@shared/generic-form/form-config';
import { ToastService } from '@core_services/toast.service';
import { environment } from '@env/environment';
import { MetaService } from '@core_services/meta.service';
import { forkJoin } from 'rxjs';

@Component({
  selector: 'app-import-profiles',
  imports: [GenericTableComponent],
  templateUrl: './import-profiles.component.html',
  styleUrls: ['./import-profiles.component.scss'],
})
export class ImportProfilesComponent implements OnInit {
  profiles: ImportProfile[] = [];
  origins: ImportOrigin[] = [];
  filterValue = '';
  isLoading = false;
  errorMessage = '';
  formFields: FormFieldConfig[] = [];
  isFormValid = false;
  columns: TableColumn<ImportProfile>[] = [];

  constructor(
    private importProfilesService: ImportProfilesService,
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
      profiles: this.importProfilesService.getProfiles(),
      origins: this.importOriginsService.getOrigins(),
      meta: this.metaService.getMeta('import-profile'),
    }).subscribe({
      next: ({ profiles, origins, meta }) => {
        this.profiles = profiles.response;
        this.origins = origins.response;
        this.formFields = meta.fields;

        this.columns = this.formFactory.getTableColumnsFromMetadata<ImportProfile>(
          this.formFields,
        );

        this.enrichColumns();

        this.isLoading = false;
      },
      error: (err: any) => {
        this.errorMessage = 'Error loading data';
        this.isLoading = false;
      },
    });
  }

  private enrichColumns() {
    if (!this.columns || this.columns.length === 0) return;
    this.columns = this.columns.map((col) => {
      if (col.key === 'origin_id') {
        return {
          ...col,
          formatter: (value: number) => this.getOriginName(value),
        };
      }
      if (col.key === 'columns') {
        return {
          ...col,
          label: 'Mappings',
          formatter: (value: any) => Object.keys(value || {}).length + ' fields',
        };
      }
      return col;
    });
  }

  getOriginName(originId: number): string {
    const origin = this.origins.find(o => o.id === originId);
    return origin ? origin.name : 'Unknown';
  }

  editProfile(profile: ImportProfile): void {
    this.openDialog(profile);
  }

  addProfile(): void {
    this.openDialog();
  }

  openDialog(data?: ImportProfile): void {
    // Update form fields with origin options
    const fieldsWithOptions = this.formFields.map(field => {
      if (field.key === 'origin_id') {
        return {
          ...field,
          options: this.origins.map(origin => ({
            value: origin.id,
            label: origin.name,
          })),
        };
      }
      return field;
    });

    const dialogRef = this.dialog.open(GenericDialogComponent, {
      data: {
        title: data ? 'Edit Profile' : 'New Profile',
        fields: fieldsWithOptions,
        initialData: data || {},
      },
    });

    dialogRef.afterClosed().subscribe((result) => {
      if (result) {
        result.id ? this.updateProfile(result) : this.createProfile(result);
      }
    });
  }

  createProfile(profile: ImportProfileCreate): void {
    this.importProfilesService.createProfile(profile).subscribe({
      next: (response) => {
        this.toastService.showToast(response, environment.toastType.Success);
        this.loadInitialData();
      },
      error: (error) => {
        this.toastService.showToast(error.error as ApiResponse<string>, environment.toastType.Error);
      }
    });
  }

  updateProfile(profile: ImportProfile): void {
    this.importProfilesService.updateProfile(profile.id, profile).subscribe({
      next: (response) => {
        this.toastService.showToast(response, environment.toastType.Success);
        this.loadInitialData();
      },
      error: (error) => {
        this.toastService.showToast(error.error as ApiResponse<string>, environment.toastType.Error);
      }
    });
  }

  deleteProfile(profile: ImportProfile): void {
    if (confirm('Are you sure you want to delete this profile?')) {
      this.importProfilesService.deleteProfile(profile.id).subscribe({
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