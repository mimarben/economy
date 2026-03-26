import { Component, Input, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { BaseChartDirective } from 'ng2-charts';
import { ChartConfiguration } from 'chart.js';
import { SummaryResponse } from '@app/services/summary.service';
import { MaterialModule } from '@app/utils/material.module';

@Component({
  selector: 'app-investment-chart',
  templateUrl: './investment-chart.component.html',
  styleUrls: ['./investment-chart.component.scss'],
  imports: [CommonModule, MaterialModule, BaseChartDirective],
  standalone: true
})
export class InvestmentChartComponent implements OnInit {
  @Input() summary!: SummaryResponse;

  chartConfig: ChartConfiguration<'pie'> = {
    type: 'pie',
    data: {
      labels: [],
      datasets: [
        {
          data: [],
          backgroundColor: [
            '#3F51B5', '#673AB7', '#9C27B0', '#E91E63', '#F06292',
            '#BA68C8', '#CE93D8', '#E1BEE7'
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
    const investments = this.summary.totals_by_category.filter(
      (item) => item.type === 'investment'
    );

    if (investments.length === 0) {
      // Show empty state
      if (this.chartConfig.data.labels) {
        this.chartConfig.data.labels = ['No data'];
      }
      if (this.chartConfig.data.datasets[0]) {
        this.chartConfig.data.datasets[0].data = [1];
        this.chartConfig.data.datasets[0].backgroundColor = ['#E0E0E0'];
      }
    } else {
      if (this.chartConfig.data.labels) {
        this.chartConfig.data.labels = investments.map((item) => item.category_name);
      }

      if (this.chartConfig.data.datasets[0]) {
        this.chartConfig.data.datasets[0].data = investments.map((item) => item.total);
      }
    }

    // Trigger change detection
    this.chartConfig = { ...this.chartConfig };
  }
}
