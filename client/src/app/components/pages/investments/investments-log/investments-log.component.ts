import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { GenericDialogComponent } from '@shared/generic-dialog/generic-dialog.component';
import { GenericTableComponent } from '@shared/generic-table/generic-table.component';
import { TableColumn } from '@shared/generic-table/generic-table.component';
import { ToastService } from '@core_services/toast.service';
import { environment } from '@environments/environment';
import { ApiResponse } from '@core_models/apiResponse';
import { InvestmentLogBase as InvestmentLog } from '@investments_models/InvestmentLogBase';
import { FormFieldConfig } from '@shared/generic-form/form-config';
import { InvestmentLogService } from '@investments_services/investment-log.service';
import { InvestmentBase as Investment } from '@investments_models/InvestmentBase';
import { InvestmentService } from '@investments_services/investment.service';
import { FormFactoryService } from '@factories/forms/form-factory.service';
import { InvestmentCategoryService } from '@investments_services/investment-category.service';
import { UtilsService } from '@utils/utils.service';
import { InvestmentCategoryBase  as InvestmentCategory} from '@investments_models/InvestmentCategoryBase';
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
  isFormValid = false;
  columns: TableColumn<InvestmentLog>[] = [];
  savingMap: Record<number, string> = [];
  constructor(
    private investmentlogService: InvestmentLogService,
    private investmentService: InvestmentService,
    private investmentCategoryService: InvestmentCategoryService,
    private utilsService: UtilsService,
    private cdr: ChangeDetectorRef,
    private dialog: MatDialog,
    private toastService: ToastService,
    private formFactory: FormFactoryService
  ) {}

  ngOnInit(): void {
    this.formFields = this.formFactory.getFormConfig('investment_log');
        this.columns = this.formFactory.getTableColumns<InvestmentLog>('investment_log', {
          saving_id: (value: number) => this.savingMap[value] ?? value,
          date: (value:string)=> this.utilsService.formatDateShortStr(value)
        });
        this.loadInvestmentLogs();
        this.loadInvestments();
  }
  loadInvestmentLogs() {
      this.isLoading = true;
      this.investmentlogService.getAll().subscribe({
        next: (data: ApiResponse<InvestmentLog[]>) => {
          this.investmentlogs = data.response;
          this.isLoading = false;
        },
        error: (err) => {
          this.errorMessage = 'Error loading saving logs';
          this.isLoading = false;
        },
      });
      this.investmentService.getAll().subscribe({
        next: (res: ApiResponse<Investment[]>) => {
          const savingField = this.formFields.find((s) => s.key === 'investment_id');
          if (savingField) {
            this.savingMap = Object.fromEntries(
              res.response.map((s) => [s.id, s.name])
            );
          }
        },
      });
    }
    private loadInvestments(): void {
      this.investmentService.getAll().subscribe({
        next: (res: ApiResponse<Investment[]>) => {
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
          this.errorMessage = 'Error loading investments';
          this.isLoading = false;
        },
      });
    }
  edit(investmentlog: InvestmentLog): void {
      this.openDialog(investmentlog);
    }
  add(): void {
      this.openDialog();
    }



  openDialog(data?: InvestmentLog): void {
    this.investmentCategoryService.getAll().subscribe({
      next:(res:ApiResponse<InvestmentCategory[]>)=>{
        const baseConfig = this.formFactory.getFormConfig('investment_log');
        const enrichedConfig = baseConfig.map(field => {
          if (field.key === 'investment_id') {
            return {
              ...field,
              options: res.response.map(r => ({
                value: r.id,
                label: r.name
              }))
            };
          }
          return field;
      });
      const dialogRef = this.dialog.open(GenericDialogComponent, {
        data: {
          title: data ? 'Edit SavingLog' : 'New SavingLog',
          fields: enrichedConfig,
          initialData: data || {},
        }
      });
      dialogRef.afterClosed().subscribe(result => {
          if (result) {
            result.id ? this.update(result) : this.create(result);
          }
        });
      },
      error: (error) => {
        console.error('Error loading data:', error);
      }
    });
  }

  update(investmentlog: InvestmentLog): void {
    this.investmentlogService.update(investmentlog.id, investmentlog).subscribe({
      next: (response: ApiResponse<InvestmentLog>) => {
        const updated = response.response;
        const index = this.investmentlogs.findIndex((h) => h.id === updated.id);
        if (index !== -1) {
          this.investmentlogs[index] = updated;
          this.investmentlogs = [...this.investmentlogs];
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

  create(investmentlog: InvestmentLog): void {
      this.investmentlogService.create(investmentlog).subscribe({
        next: (response: ApiResponse<InvestmentLog>) => {
          this.investmentlogs.push(response.response);
          this.investmentlogs = [...this.investmentlogs];
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
