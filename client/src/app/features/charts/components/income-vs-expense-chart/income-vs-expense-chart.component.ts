import { Component, Input, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { BaseChartDirective } from 'ng2-charts';
import { ChartConfiguration } from 'chart.js';
import { SummaryResponse } from '@app/services/summary.service';
import { MATERIAL_IMPORTS } from '@app/utils/material.imports';
import { ChartExportService } from '@app/services/export/chart-export.service';

@Component({
  selector: 'app-income-vs-expense-chart',
  templateUrl: './income-vs-expense-chart.component.html',
  styleUrls: ['./income-vs-expense-chart.component.scss'],
  imports: [CommonModule, ...MATERIAL_IMPORTS, BaseChartDirective],
  standalone: true
})
export class IncomeVsExpenseChartComponent implements OnInit {
  @Input() summary!: SummaryResponse;

  constructor(private exportSvc: ChartExportService) {}

  export(): void {
    const { total_income, total_expense, net, count_transactions } = this.summary.income_vs_expense;
    const rows = [
      { Type: 'Income',   Amount: total_income },
      { Type: 'Expenses', Amount: total_expense },
      { Type: 'Net',      Amount: net },
      { Type: 'Transactions', Amount: count_transactions },
    ];
    this.exportSvc.exportToExcel(rows, 'income-vs-expenses');
  }

  chartConfig: ChartConfiguration<'bar'> = {
    type: 'bar',
    data: {
      labels: ['Income', 'Expenses', 'Net'],
      datasets: [
        {
          label: 'Amount',
          data: [],
          backgroundColor: ['#4CAF50', '#FF6384', '#2196F3'],
          borderColor: ['#388E3C', '#E53935', '#1565C0'],
          borderWidth: 2,
          borderRadius: 6,
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: (context) => `€${(context.parsed.y as number).toFixed(2)}`
          }
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            callback: (value) => `€${value}`
          }
        }
      }
    }
  };

  ngOnInit(): void {
    this.updateChart();
  }

  private updateChart(): void {
    const { total_income, total_expense, net } = this.summary.income_vs_expense;

    if (this.chartConfig.data.datasets[0]) {
      this.chartConfig.data.datasets[0].data = [total_income, total_expense, net];
    }

    this.chartConfig = { ...this.chartConfig };
  }
}
