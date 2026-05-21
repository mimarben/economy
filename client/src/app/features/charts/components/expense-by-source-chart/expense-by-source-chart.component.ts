import { Component, Input, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { BaseChartDirective } from 'ng2-charts';
import { ChartConfiguration } from 'chart.js';
import { SummaryResponse } from '@app/services/summary.service';
import { MATERIAL_IMPORTS } from '@app/utils/material.imports';
import { ChartExportService } from '@app/services/export/chart-export.service';

@Component({
  selector: 'app-expense-by-source-chart',
  templateUrl: './expense-by-source-chart.component.html',
  styleUrls: ['./expense-by-source-chart.component.scss'],
  imports: [CommonModule, ...MATERIAL_IMPORTS, BaseChartDirective],
  standalone: true
})
export class ExpenseBySourceChartComponent implements OnInit {
  @Input() summary!: SummaryResponse;

  constructor(private exportSvc: ChartExportService) {}

  export(): void {
    const rows = this.summary.totals_by_source.map((s) => ({
      Source: s.source_name,
      Type: s.type,
      Amount: s.total,
    }));
    this.exportSvc.exportToExcel(rows, 'transactions-by-source');
  }

  chartConfig: ChartConfiguration<'bar'> = {
    type: 'bar',
    data: {
      labels: [],
      datasets: [
        {
          label: 'Expenses',
          data: [],
          backgroundColor: 'rgba(255, 99, 132, 0.8)',
          borderColor: '#E53935',
          borderWidth: 1,
          borderRadius: 4,
        },
        {
          label: 'Income',
          data: [],
          backgroundColor: 'rgba(76, 175, 80, 0.8)',
          borderColor: '#388E3C',
          borderWidth: 1,
          borderRadius: 4,
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      indexAxis: 'y',
      plugins: {
        legend: {
          position: 'top',
          labels: { padding: 15, font: { size: 12 } }
        },
        tooltip: {
          callbacks: {
            label: (context) => `${context.dataset.label}: €${(context.parsed.x as number).toFixed(2)}`
          }
        }
      },
      scales: {
        x: {
          beginAtZero: true,
          ticks: { callback: (value) => `€${value}` }
        }
      }
    }
  };

  ngOnInit(): void {
    this.updateChart();
  }

  private updateChart(): void {
    const sources = this.summary.totals_by_source;

    const sourceNames = [...new Set(sources.map((s) => s.source_name))];

    const expenseMap = new Map(
      sources.filter((s) => s.type === 'expense').map((s) => [s.source_name, s.total])
    );
    const incomeMap = new Map(
      sources.filter((s) => s.type === 'income').map((s) => [s.source_name, s.total])
    );

    if (this.chartConfig.data.labels) {
      this.chartConfig.data.labels = sourceNames;
    }
    this.chartConfig.data.datasets[0].data = sourceNames.map((n) => expenseMap.get(n) ?? 0);
    this.chartConfig.data.datasets[1].data = sourceNames.map((n) => incomeMap.get(n) ?? 0);

    this.chartConfig = { ...this.chartConfig };
  }
}
