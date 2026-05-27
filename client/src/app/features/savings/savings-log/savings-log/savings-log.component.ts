import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { forkJoin } from 'rxjs';
import { GenericDialogComponent } from '@shared/generic-dialog/generic-dialog.component';
import { SavingLogBase as SavingLog } from '@savings_models/SavingLogBase';
import { SavingBase as Saving } from '@savings_models/SavingBase';
import { SourceBase as Source } from '@finance_models/SourceBase';
import { GenericTableComponent, TableColumn } from '@shared/generic-table/generic-table.component';
import { ApiResponse } from '@app/models/core/APIResponse';
import { FormFactoryService } from '@app/core/factories/form-factory.service';
import { FormFieldConfig } from '@shared/generic-form/form-config';
import { ToastService } from '@core_services/toast.service';
import { environment } from '@env/environment';
import { SavingLogService } from '@savings_services/saving-log.service';
import { SavingService } from '@savings_services/saving.service';
import { UtilsService } from '@app/utils/utils.service';
import { SourceService } from '@finance_services/source.service';
import { MetaService } from '@core_services/meta.service';

@Component({
  selector: 'app-savings-log',
  imports: [GenericTableComponent],
  templateUrl: './savings-log.component.html',
  styleUrl: './savings-log.component.css',
})
export class SavingsLogComponent implements OnInit {
  savinglogs: SavingLog[] = [];
  filterValue = '';
  isLoading = false;
  errorMessage = '';
  formFields: FormFieldConfig[] = [];
  isFormValid = false;
  columns: TableColumn<SavingLog>[] = [];
  savingMap: Record<number, string> = {};

  constructor(
    private savinglogService: SavingLogService,
    private savingService: SavingService,
    private sourceService: SourceService,
    private metaService: MetaService,
    private utilsService: UtilsService,
    private cdr: ChangeDetectorRef,
    private dialog: MatDialog,
    private toastService: ToastService,
    private formFactory: FormFactoryService,
  ) {}

  ngOnInit(): void {
    this.loadInitialData();
  }

  private loadInitialData(): void {
    this.isLoading = true;
    forkJoin({
      logs: this.savinglogService.getAll(),
      meta: this.metaService.getMeta('saving-log'),
      savings: this.savingService.getAll(),
      sources: this.sourceService.getAll(),
    }).subscribe({
      next: ({ logs, meta, savings, sources }) => {
        this.savinglogs = logs.response;

        this.savingMap = Object.fromEntries(
          savings.response.map((s: Saving) => [s.id as number, s.description || ''])
        );

        const relationOptions = {
          saving: savings.response.map((s: Saving) => ({ value: s.id as number, label: s.description || '' })),
          source: sources.response.map((s: Source) => ({ value: s.id as number, label: s.name })),
        };

        this.formFields = this.formFactory.enrichMetadataFields(meta.fields, relationOptions);
        const baseCols = this.formFactory.getTableColumnsFromMetadata<SavingLog>(this.formFields);
        this.columns = baseCols.map((col) => {
          if (col.key === 'saving_id') return { ...col, formatter: (v: number) => this.savingMap[v] ?? String(v) };
          if (col.key === 'date') return { ...col, formatter: (v: string) => this.utilsService.formatDateShortStr(v) };
          return col;
        });

        this.isLoading = false;
      },
      error: () => {
        this.errorMessage = 'Error loading saving logs';
        this.isLoading = false;
      },
    });
  }

  editSavingLog(savinglog: SavingLog): void {
    this.openDialog(savinglog);
  }

  addSavingLog(): void {
    this.openDialog();
  }

  openDialog(data?: SavingLog): void {
    const dialogRef = this.dialog.open(GenericDialogComponent, {
      data: {
        title: data ? 'Edit Saving Log' : 'New Saving Log',
        fields: this.formFields,
        initialData: data || {},
      },
    });

    dialogRef.afterClosed().subscribe((result) => {
      if (result) {
        result.id ? this.updateSavingLog(result) : this.createSavingLog(result);
      }
    });
  }

  updateSavingLog(savinglog: SavingLog): void {
    this.savinglogService.update(savinglog.id!, savinglog).subscribe({
      next: (response: ApiResponse<SavingLog>) => {
        const updated = response.response;
        const index = this.savinglogs.findIndex((s) => s.id === updated.id);
        if (index !== -1) {
          this.savinglogs[index] = updated;
          this.savinglogs = [...this.savinglogs];
        }
        this.toastService.showToast(response, environment.toastType.Success, {});
        this.cdr.detectChanges();
      },
      error: (err) => {
        this.toastService.showToast(err.error as ApiResponse<string>, environment.toastType.Error, {});
      },
    });
  }

  createSavingLog(savinglog: SavingLog): void {
    this.savinglogService.create(savinglog).subscribe({
      next: (response: ApiResponse<SavingLog>) => {
        this.savinglogs.push(response.response);
        this.savinglogs = [...this.savinglogs];
        this.toastService.showToast(response, environment.toastType.Success, {});
        this.cdr.detectChanges();
      },
      error: (err) => {
        this.toastService.showToast(err.error as ApiResponse<string>, environment.toastType.Error, {});
      },
    });
  }

  applyFilter(event: Event) {
    this.filterValue = (event.target as HTMLInputElement).value.trim().toLowerCase();
  }
}
