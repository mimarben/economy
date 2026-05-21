import { Component, Input, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { BaseChartDirective } from 'ng2-charts';
import { ChartConfiguration } from 'chart.js';
import { SummaryResponse } from '@app/services/summary.service';
import { MATERIAL_IMPORTS } from '@app/utils/material.imports';
import { ChartExportService } from '@app/services/export/chart-export.service';

const USER_COLORS = [
  'rgba(33, 150, 243, 0.8)',
  'rgba(255, 152, 0, 0.8)',
  'rgba(156, 39, 176, 0.8)',
  'rgba(0, 188, 212, 0.8)',
  'rgba(233, 30, 99, 0.8)',
  'rgba(139, 195, 74, 0.8)',
];

@Component({
  selector: 'app-expense-by-user-chart',
  templateUrl: './expense-by-user-chart.component.html',
  styleUrls: ['./expense-by-user-chart.component.scss'],
  imports: [CommonModule, ...MATERIAL_IMPORTS, BaseChartDirective],
  standalone: true
})
export class ExpenseByUserChartComponent implements OnInit {
  @Input() summary!: SummaryResponse;

  constructor(private exportSvc: ChartExportService) {}

  export(): void {
    const rows = this.summary.totals_by_user.map((u) => ({
      User: u.user_name,
      Total: u.total,
    }));
    this.exportSvc.exportToExcel(rows, 'expenses-by-user');
  }

  chartConfig: ChartConfiguration<'doughnut'> = {
    type: 'doughnut',
    data: {
      labels: [],
      datasets: [
        {
          data: [],
          backgroundColor: USER_COLORS,
          borderColor: 'rgba(255, 255, 255, 1)',
          borderWidth: 2,
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'bottom',
          labels: { padding: 15, font: { size: 12 } }
        },
        tooltip: {
          callbacks: {
            label: (context) => {
              const label = context.label || '';
              const value = context.parsed || 0;
              return `${label}: €${value.toFixed(2)}`;
            }
          }
        }
      }
    }
  };

  ngOnInit(): void {
    this.updateChart();
  }

  private updateChart(): void {
    const users = this.summary.totals_by_user;

    if (this.chartConfig.data.labels) {
      this.chartConfig.data.labels = users.map((u) => u.user_name);
    }
    if (this.chartConfig.data.datasets[0]) {
      this.chartConfig.data.datasets[0].data = users.map((u) => u.total);
    }

    this.chartConfig = { ...this.chartConfig };
  }
}
