import { Component, Input, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { BaseChartDirective } from 'ng2-charts';
import { ChartConfiguration } from 'chart.js';
import { SummaryResponse } from '@app/services/summary.service';
import { MATERIAL_IMPORTS } from '@app/utils/material.imports';

@Component({
  selector: 'app-expense-chart',
  templateUrl: './expense-chart.component.html',
  styleUrls: ['./expense-chart.component.scss'],
  imports: [CommonModule, ...MATERIAL_IMPORTS, BaseChartDirective],
  standalone: true
})
export class ExpenseChartComponent implements OnInit {
  @Input() summary!: SummaryResponse;

  chartConfig: ChartConfiguration<'doughnut'> = {
    type: 'doughnut',
    data: {
      labels: [],
      datasets: [
        {
          data: [],
          backgroundColor: [
            '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF',
            '#FF9F40', '#FF6384', '#C9CBCF'
          ],
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
          labels: {
            padding: 15,
            font: { size: 12 }
          }
        },
        tooltip: {
          callbacks: {
            label: (context) => {
              const label = context.label || '';
              const value = context.parsed || 0;
              return `${label}: $${value.toFixed(2)}`;
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
    const expenses = this.summary.totals_by_category.filter(
      (item) => item.type === 'expense'
    );

    if (this.chartConfig.data.labels) {
      this.chartConfig.data.labels = expenses.map((item) => item.category_name);
    }

    if (this.chartConfig.data.datasets[0]) {
      this.chartConfig.data.datasets[0].data = expenses.map((item) => item.total);
    }

    // Trigger change detection
    this.chartConfig = { ...this.chartConfig };
  }
}
