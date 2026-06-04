import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { forkJoin } from 'rxjs';
import { GenericDialogComponent } from '@shared/generic-dialog/generic-dialog.component';
import { GenericTableComponent, TableColumn } from '@shared/generic-table/generic-table.component';
import { ToastService } from '@core_services/toast.service';
import { environment } from '@env/environment';
import { ApiResponse } from '@app/models/core/APIResponse';
import { InvestmentLogBase as InvestmentLog } from '@investments_models/InvestmentLogBase';
import { InvestmentBase as Investment } from '@investments_models/InvestmentBase';
import { FormFieldConfig } from '@shared/generic-form/form-config';
import { InvestmentLogService } from '@investments_services/investment-log.service';
import { InvestmentService } from '@investments_services/investment.service';
import { FormFactoryService } from '@app/core/factories/form-factory.service';
import { MetaService } from '@core_services/meta.service';
import { UtilsService } from '@app/utils/utils.service';

@Component({
  selector: 'app-investments-log',
  imports: [GenericTableComponent],
  templateUrl: './investments-log.component.html',
  styleUrl: './investments-log.component.css'
})
export class InvestmentsLogComponent implements OnInit {
  investmentlogs: InvestmentLog[] = [];
  filterValue = '';
  isLoading = false;
  errorMessage = '';
  formFields: FormFieldConfig[] = [];
  columns: TableColumn<InvestmentLog>[] = [];
  investmentMap: Record<number, string> = {};

  constructor(
    private investmentlogService: InvestmentLogService,
    private investmentService: InvestmentService,
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
      logs: this.investmentlogService.getAll(),
      meta: this.metaService.getMeta('investment-log'),
      investments: this.investmentService.getAll(),
    }).subscribe({
      next: ({ logs, meta, investments }) => {
        this.investmentlogs = (logs.response as InvestmentLog[]).sort(
          (a, b) => new Date(b.date).getTime() - new Date(a.date).getTime()
        );

        this.investmentMap = Object.fromEntries(
          investments.response.map((i: Investment) => [i.id as number, i.description])
        );

        const relationOptions = {
          investment: investments.response.map((i: Investment) => ({ value: i.id as number, label: i.description })),
        };

        this.formFields = this.formFactory.enrichMetadataFields(meta.fields, relationOptions);
        const baseCols = this.formFactory.getTableColumnsFromMetadata<InvestmentLog>(this.formFields);
        this.columns = baseCols.map((col) => {
          if (col.key === 'investment_id') return { ...col, formatter: (v: number) => this.investmentMap[v] ?? String(v) };
          if (col.key === 'date') return { ...col, formatter: (v: string) => this.utilsService.formatDateShortStr(v) };
          return col;
        });

        this.isLoading = false;
        this.cdr.detectChanges();
      },
      error: () => {
        this.errorMessage = 'Error loading investment logs';
        this.isLoading = false;
      },
    });
  }

  openDialog(data?: Partial<InvestmentLog>): void {
    const dialogRef = this.dialog.open(GenericDialogComponent, {
      data: {
        title: data?.id ? 'Edit Investment Log' : 'New Investment Log',
        fields: this.formFields,
        initialData: data || { date: new Date() },
      },
    });

    dialogRef.afterClosed().subscribe((result) => {
      if (result) {
        result.id ? this.update(result) : this.create(result);
      }
    });
  }

  edit(investmentlog: InvestmentLog): void {
    this.openDialog(investmentlog);
  }

  add(): void {
    this.openDialog();
  }

  duplicate(investmentlog: InvestmentLog): void {
    const { id: _id, ...copy } = investmentlog as any;
    this.openDialog(copy);
  }

  deleteLog(investmentlog: InvestmentLog): void {
    if (!confirm('Delete this investment log entry?')) return;
    this.investmentlogService.delete(investmentlog.id!).subscribe({
      next: () => {
        this.investmentlogs = this.investmentlogs.filter(l => l.id !== investmentlog.id);
        this.cdr.detectChanges();
      },
      error: (err) => {
        this.toastService.showToast(err.error as ApiResponse<string>, environment.toastType.Error, {});
      },
    });
  }

  update(investmentlog: InvestmentLog): void {
    this.investmentlogService.update(investmentlog.id!, investmentlog).subscribe({
      next: (response: ApiResponse<InvestmentLog>) => {
        const updated = response.response;
        const index = this.investmentlogs.findIndex((h) => h.id === updated.id);
        if (index !== -1) {
          this.investmentlogs[index] = updated;
          this.investmentlogs = [...this.investmentlogs];
        }
        this.toastService.showToast(response, environment.toastType.Success, {});
        this.cdr.detectChanges();
      },
      error: (err) => {
        this.toastService.showToast(err.error as ApiResponse<string>, environment.toastType.Error, {});
      },
    });
  }

  create(investmentlog: InvestmentLog): void {
    this.investmentlogService.create(investmentlog).subscribe({
      next: (response: ApiResponse<InvestmentLog>) => {
        this.investmentlogs.push(response.response);
        this.investmentlogs = [...this.investmentlogs];
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
