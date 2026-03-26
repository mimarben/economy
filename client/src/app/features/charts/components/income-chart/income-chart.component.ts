import { Component, Input, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { BaseChartDirective } from 'ng2-charts';
import { ChartConfiguration } from 'chart.js';
import { SummaryResponse } from '@app/services/summary.service';
import { MaterialModule } from '@app/utils/material.module';

@Component({
  selector: 'app-income-chart',
  templateUrl: './income-chart.component.html',
  styleUrls: ['./income-chart.component.scss'],
  imports: [CommonModule, MaterialModule, BaseChartDirective],
  standalone: true
})
export class IncomeChartComponent implements OnInit {
  @Input() summary!: SummaryResponse;

  chartConfig: ChartConfiguration<'doughnut'> = {
    type: 'doughnut',
    data: {
      labels: [],
      datasets: [
        {
          data: [],
          backgroundColor: [
            '#4CAF50', '#8BC34A', '#CDDC39', '#FFC107', '#FF9800',
            '#FF5722', '#00BCD4', '#009688'
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
    const incomes = this.summary.totals_by_category.filter(
      (item) => item.type === 'income'
    );

    if (this.chartConfig.data.labels) {
      this.chartConfig.data.labels = incomes.map((item) => item.category_name);
    }

    if (this.chartConfig.data.datasets[0]) {
      this.chartConfig.data.datasets[0].data = incomes.map((item) => item.total);
    }

    // Trigger change detection
    this.chartConfig = { ...this.chartConfig };
  }
}
