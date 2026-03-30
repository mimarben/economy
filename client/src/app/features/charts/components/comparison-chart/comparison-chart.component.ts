import { Component, Input, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { BaseChartDirective } from 'ng2-charts';
import { ChartConfiguration } from 'chart.js';
import { SummaryResponse } from '@app/services/summary.service';
import { MATERIAL_IMPORTS } from '@app/utils/material.imports';

@Component({
  selector: 'app-comparison-chart',
  templateUrl: './comparison-chart.component.html',
  styleUrls: ['./comparison-chart.component.scss'],
  imports: [CommonModule, ...MATERIAL_IMPORTS, BaseChartDirective],
  standalone: true
})
export class ComparisonChartComponent implements OnInit {
  @Input() summary!: SummaryResponse;

  chartConfig: ChartConfiguration<'line'> = {
    type: 'line',
    data: {
      labels: [],
      datasets: [
        {
          label: 'Income',
          data: [],
          borderColor: '#4CAF50',
          backgroundColor: 'rgba(76, 175, 80, 0.1)',
          tension: 0.3,
          fill: true,
        },
        {
          label: 'Expense',
          data: [],
          borderColor: '#FF6384',
          backgroundColor: 'rgba(255, 99, 132, 0.1)',
          tension: 0.3,
          fill: true,
        },
        {
          label: 'Net',
          data: [],
          borderColor: '#2196F3',
          backgroundColor: 'rgba(33, 150, 243, 0)',
          tension: 0.3,
          fill: false,
          borderWidth: 2,
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top',
          labels: {
            padding: 15,
            font: { size: 12 }
          }
        },
        tooltip: {
          mode: 'index',
          intersect: false,
          callbacks: {
            label: (context) => {
              const label = context.dataset.label || '';
              const value = context.parsed.y || 0;
              return `${label}: $${value.toFixed(2)}`;
            }
          }
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            callback: (value) => `$${value}`
          }
        }
      }
    }
  };

  ngOnInit(): void {
    this.updateChart();
  }

  private updateChart(): void {
    const timeData = this.summary.totals_over_time;

    if (this.chartConfig.data.labels) {
      this.chartConfig.data.labels = timeData.map((item) =>
        new Date(item.date).toLocaleDateString('en-US', {
          month: 'short',
          day: 'numeric'
        })
      );
    }

    if (this.chartConfig.data.datasets) {
      // Income
      this.chartConfig.data.datasets[0].data = timeData.map((item) => item.income);
      // Expense
      this.chartConfig.data.datasets[1].data = timeData.map((item) => item.expense);
      // Net
      this.chartConfig.data.datasets[2].data = timeData.map((item) => item.net);
    }

    // Trigger change detection
    this.chartConfig = { ...this.chartConfig };
  }
}
