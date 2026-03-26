import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { SummaryService, SummaryResponse, PeriodType } from '@app/services/summary.service';
import { Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';
import { MaterialModule } from '@app/utils/material.module';
import { ExpenseChartComponent } from '../expense-chart/expense-chart.component';
import { IncomeChartComponent } from '../income-chart/income-chart.component';
import { InvestmentChartComponent } from '../investment-chart/investment-chart.component';
import { ComparisonChartComponent } from '../comparison-chart/comparison-chart.component';

@Component({
  selector: 'app-charts-container',
  templateUrl: './charts-container.component.html',
  styleUrls: ['./charts-container.component.scss'],
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MaterialModule,
    ExpenseChartComponent,
    IncomeChartComponent,
    InvestmentChartComponent,
    ComparisonChartComponent
  ],
  standalone: true
})
export class ChartsContainerComponent implements OnInit, OnDestroy {
  filterForm: FormGroup;
  summary: SummaryResponse | null = null;
  loading = false;
  error: string | null = null;
  periodType: PeriodType = 'month';
  private destroy$ = new Subject<void>();

  constructor(
    private fb: FormBuilder,
    private summaryService: SummaryService
  ) {
    this.filterForm = this.fb.group({
      period: ['month'],
      startDate: [null],
      endDate: [null],
    });
  }

  ngOnInit(): void {
    // Load default month summary
    this.loadMonthlySummary();

    // Subscribe to period changes
    this.filterForm.get('period')?.valueChanges
      .pipe(takeUntil(this.destroy$))
      .subscribe((period) => {
        this.periodType = period;
        this.onPeriodChange();
      });
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  onPeriodChange(): void {
    switch (this.periodType) {
      case 'week':
        this.loadWeeklySummary();
        break;
      case 'month':
        this.loadMonthlySummary();
        break;
      case 'year':
        this.loadYearlySummary();
        break;
      case 'custom':
        this.enableCustomDateRange();
        break;
    }
  }

  loadCustomRange(): void {
    const startDate = this.filterForm.get('startDate')?.value;
    const endDate = this.filterForm.get('endDate')?.value;

    if (!startDate || !endDate) {
      this.error = 'Please select both start and end dates';
      return;
    }

    const formattedStart = this.formatDate(startDate);
    const formattedEnd = this.formatDate(endDate);

    this.loading = true;
    this.summaryService.getSummary(formattedStart, formattedEnd)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (response) => {
          this.summary = response.data;
          this.loading = false;
          this.error = null;
        },
        error: (err) => {
          this.error = err.error?.error || 'Failed to load summary';
          this.loading = false;
        },
      });
  }

  private loadWeeklySummary(): void {
    this.loading = true;
    this.summaryService.getWeekSummary()
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (response) => {
          this.summary = response.data;
          this.loading = false;
          this.error = null;
        },
        error: (err) => {
          this.error = err.error?.error || 'Failed to load week summary';
          this.loading = false;
        },
      });
  }

  private loadMonthlySummary(): void {
    this.loading = true;
    this.summaryService.getMonthSummary()
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (response) => {
          this.summary = response.data;
          this.loading = false;
          this.error = null;
        },
        error: (err) => {
          this.error = err.error?.error || 'Failed to load month summary';
          this.loading = false;
        },
      });
  }

  private loadYearlySummary(): void {
    this.loading = true;
    this.summaryService.getYearSummary()
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (response) => {
          this.summary = response.data;
          this.loading = false;
          this.error = null;
        },
        error: (err) => {
          this.error = err.error?.error || 'Failed to load year summary';
          this.loading = false;
        },
      });
  }

  private enableCustomDateRange(): void {
    this.filterForm.get('startDate')?.enable();
    this.filterForm.get('endDate')?.enable();
  }

  private formatDate(date: Date): string {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  }
}
