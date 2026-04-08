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
        }).map((field) =>
          field.key === 'columns'
            ? { ...field, type: 'text', label: 'Column mappings' }
            : field,
        );

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
          formatter: (value: any) => this.getColumnsPreview(value),
          tooltipFormatter: (value: any) => this.getColumnsTooltip(value),
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
    const isEditing = !!data?.id;
    const dialogRef = this.dialog.open(GenericDialogComponent, {
      width: '800px',
      data: {
        title: data ? 'Edit Profile' : 'New Profile',
        fields: this.formFields,
        initialData: data
          ? {
              ...data,
              columns: typeof data.columns === 'string'
                ? JSON.parse(data.columns || '{}')
                : (data.columns ?? {}),
            }
          : { columns: {} },
      },
    });

    dialogRef.afterClosed().subscribe((result) => {
      if (result) {
        isEditing ? this.updateProfile(data!.id, result) : this.createProfile(result);
      }
    });
  }

  private toProfilePayload(profile: Partial<ImportProfile>): ImportProfileCreate | null {
    const parsedColumns = this.parseColumns(profile.columns);
    if (parsedColumns === null) {
      return null;
    }

    const payload: ImportProfileCreate = {
      origin_id: Number(profile.origin_id),
      name: profile.name ?? '',
      header_row_guess: profile.header_row_guess ?? 1,
      columns: parsedColumns,
      active: profile.active ?? true,
    };

    // Solo incluir file_type si existe
    if (profile['file_type']) {
      (payload as any)['file_type'] = profile['file_type'];
    }

    return payload;
  }

  createProfile(profile: Partial<ImportProfile>): void {
    const payload = this.toProfilePayload(profile);
    if (!payload) return;

    this.importProfilesService.createProfile(payload).subscribe({
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
    const payload = this.toProfilePayload(profile);
    if (!payload) return;

    const updatePayload: ImportProfileUpdate = payload;
    this.importProfilesService.updateProfile(id, updatePayload).subscribe({
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

  private getColumnsPreview(value: unknown): string {
    const columns = this.parseColumns(value, false);
    if (!columns) return 'Invalid format';
    const keys = Object.keys(columns);
    if (!keys.length) return 'No mappings';

    return keys.slice(0, 4).join(', ');
  }

  private getColumnsTooltip(value: unknown): string {
    const columns = this.parseColumns(value, false);
    if (!columns) return 'Invalid columns JSON';
    return Object.entries(columns)
      .map(([key, aliases]) => `${key}: ${(aliases || []).join(', ')}`)
      .join('\n');
  }

  private parseColumns(
    value: unknown,
    showError = true,
  ): Record<string, string[]> | null {
    try {
      // Si está vacío, retornar un objeto vacío
      if (!value || (typeof value === 'string' && value.trim() === '')) {
        return {};
      }

      const parsed =
        typeof value === 'string'
          ? JSON.parse(value)
          : (value ?? {});

      if (!parsed || typeof parsed !== 'object' || Array.isArray(parsed)) {
        throw new Error('Columns must be a JSON object');
      }

      return Object.fromEntries(
        Object.entries(parsed as Record<string, unknown>).map(([key, aliases]) => [
          key,
          Array.isArray(aliases) ? aliases.map((item) => String(item)) : [],
        ]),
      );
    } catch (error) {
      if (showError) {
        this.toastService.error('Columns JSON is not valid. Example: { "date": ["fecha"] }');
      }
      return null;
    }
  }
}
