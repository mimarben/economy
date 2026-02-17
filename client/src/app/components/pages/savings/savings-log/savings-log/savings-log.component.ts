import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { forkJoin } from 'rxjs';
import { GenericDialogComponent } from '@shared/generic-dialog/generic-dialog.component';
import { SavingLogBase as SavingLog } from '@savings_models/SavingLogBase';
import { SavingBase as Saving } from '@savings_models/SavingBase';
import {
  GenericTableComponent,
  TableColumn,
} from '@shared/generic-table/generic-table.component';
import { ApiResponse } from '@core_models/apiResponse';
import { FormFactoryService } from '@factories/forms/form-factory.service';
import { FormFieldConfig } from '@shared/generic-form/form-config';
import { ToastService } from '@core_services/toast.service';
import { environment } from '@environments/environment';
import { SavingLogService } from '@savings_services/saving-log.service';
import { SavingService } from '@savings_services/saving.service';
import { UtilsService } from '@utils/utils.service';
import { SourceService } from '@finance_services/source.service';

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
  savingMap: Record<number, string> = [];
  constructor(
    private savinglogService: SavingLogService,
    private savingService: SavingService,
    private utilsService: UtilsService,
    private cdr: ChangeDetectorRef,
    private dialog: MatDialog,
    private toastService: ToastService,
    private formFactory: FormFactoryService,
    private sourceService: SourceService
  ) {}
  ngOnInit(): void {
    this.formFields = this.formFactory.getFormConfig('saving_log');
    this.columns = this.formFactory.getTableColumns<SavingLog>('saving_log', {
      saving_id: (value: number) => this.savingMap[value] ?? value,
      date: (value:string)=> this.utilsService.formatDateShortStr(value)
    });
    this.loadSavingLogs();
    this.loadSavings();
  }
  loadSavingLogs() {
    this.isLoading = true;
    this.savinglogService.getAll().subscribe({
      next: (data: ApiResponse<SavingLog[]>) => {
        this.savinglogs = data.response;
        this.isLoading = false;
      },
      error: (err) => {
        this.errorMessage = 'Error loading saving logs';
        this.isLoading = false;
      },
    });
    this.savingService.getAll().subscribe({
      next: (res: ApiResponse<Saving[]>) => {
        const savingField = this.formFields.find((s) => s.key === 'saving_id');
        if (savingField) {
          this.savingMap = Object.fromEntries(
            res.response.map((s) => [s.id, s.name])
          );
        }
      },
    });
  }
  private loadSavings(): void {
    this.savingService.getAll().subscribe({
      next: (res: ApiResponse<Saving[]>) => {
        const field = this.formFields.find((f) => f.key === 'saving_id');
        if (field) {
          field.type = 'select';
          field.options = res.response.map(s => ({
            label: `${s.name}`,
            value: s.id,
          }));
        }
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
    // 1. Cargar TODO en paralelo antes de abrir el diálogo
    forkJoin({
      savings: this.savingService.getAll(),
      sources: this.sourceService.getAll()
    }).subscribe({
      next: (responses) => {
        const baseConfig = this.formFactory.getFormConfig('saving_log');

        // 2. Enriquecer directamente los campos con las opciones
        const enrichedConfig = baseConfig.map(field => {
          if (field.key === 'saving_id') {
            return {
              ...field,
              options: responses.savings.response.map(r => ({
                value: r.id,
                label: r.description
              }))
            };
          }

          if (field.key === 'source_id') {
            return {
              ...field,
              options: responses.sources.response.map(r => ({
                value: r.id,
                label: `${r.name}`
              }))
            };
          }

          return field;
        });

        // 3. Abrir el diálogo SOLO cuando los datos estén listos
        const dialogRef = this.dialog.open(GenericDialogComponent, {
          data: {
            title: data ? 'Edit Household Member' : 'New Household Member',
            fields: enrichedConfig,
            initialData: data || {}
          }
        });

        dialogRef.afterClosed().subscribe(result => {
          if (result) {
            result.id ? this.updateSavingLog(result) : this.createSavingLog(result);
          }
        });
      },
      error: (error) => {
        console.error('Error loading data:', error);
      }
    });
  }
/*  openDialog(data?: SavingLog): void {
    const dialogRef = this.dialog.open(GenericDialogComponent, {
      data: {
        title: data ? 'Edit SavingLog' : 'New SavingLog',
        fields: this.formFactory.getFormConfig('saving_log'),
        initialData: data || {},
      },
    });

    dialogRef.afterClosed().subscribe((result) => {
      if (result) {
        result.id ? this.updateSavingLog(result) : this.createSavingLog(result);
      }
    });
  } */

  updateSavingLog(savinglog: SavingLog): void {
    this.savinglogService.update(savinglog.id, savinglog).subscribe({
      next: (response: ApiResponse<SavingLog>) => {
        const updated = response.response;
        const index = this.savinglogs.findIndex((h) => h.id === updated.id);
        if (index !== -1) {
          this.savinglogs[index] = updated;
          this.savinglogs = [...this.savinglogs];
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
  createSavingLog(savinglog: SavingLog): void {
    this.savinglogService.create(savinglog).subscribe({
      next: (response: ApiResponse<SavingLog>) => {
        this.savinglogs.push(response.response);
        this.savinglogs = [...this.savinglogs];
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
