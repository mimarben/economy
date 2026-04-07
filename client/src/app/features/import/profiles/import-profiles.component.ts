import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { ImportProfileBase as ImportProfile } from '@app/models/import/import-profileBase';
import { ImportOriginBase as ImportOrigin } from '@app/models/import/import-originBase';
import { GenericTableComponent, TableColumn } from '@shared/generic-table/generic-table.component';
import { ApiResponse } from '@app/models/core/APIResponse';
import { GenericDialogComponent } from '@shared/generic-dialog/generic-dialog.component';
import { FormFactoryService } from '@app/core/factories/form-factory.service';
import {
  ImportProfilesService,
  ImportOriginsService,
  ImportProfileCreate,
  ImportProfileUpdate,
} from '@import_services/import-profiles.service';
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
        this.formFields = this.formFactory.enrichMetadataFields(meta.fields, {
          origin: this.origins.map((origin) => ({
            value: origin.id,
            label: origin.name,
          })),
          origin_id: this.origins.map((origin) => ({
            value: origin.id,
            label: origin.name,
          })),
        });

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
    const selectOptionsMap = Object.fromEntries(
      this.formFields
        .filter((field) => field.type === 'select' && field.options?.length)
        .map((field) => [field.key, field.options ?? []]),
    ) as Record<string, { value: string | number; label: string }[]>;

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
      if (col.key.endsWith('_id') && selectOptionsMap[col.key]) {
        return {
          ...col,
          formatter: (value: string | number) =>
            selectOptionsMap[col.key].find((opt) => opt.value === value)?.label ??
            String(value ?? '—'),
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
    const dialogRef = this.dialog.open(GenericDialogComponent, {
      data: {
        title: data ? 'Edit Profile' : 'New Profile',
        fields: this.formFields,
        initialData: data || {},
      },
    });

    dialogRef.afterClosed().subscribe((result) => {
      if (result) {
        result.id ? this.updateProfile(result.id, result) : this.createProfile(result);
      }
    });
  }

  private toProfilePayload(profile: Partial<ImportProfile>): ImportProfileCreate {
    return {
      origin_id: Number(profile.origin_id),
      name: profile.name ?? '',
      header_row_guess: profile.header_row_guess ?? 1,
      columns: profile.columns ?? {},
      active: profile.active ?? true,
    };
  }

  createProfile(profile: Partial<ImportProfile>): void {
    this.importProfilesService.createProfile(this.toProfilePayload(profile)).subscribe({
      next: (response) => {
        this.toastService.showToast(response, environment.toastType.Success);
        this.loadInitialData();
      },
      error: (error) => {
        this.toastService.showToast(error.error as ApiResponse<string>, environment.toastType.Error);
      }
    });
  }

  updateProfile(id: number, profile: Partial<ImportProfile>): void {
    const payload: ImportProfileUpdate = this.toProfilePayload(profile);
    this.importProfilesService.updateProfile(id, payload).subscribe({
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
