import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MATERIAL_IMPORTS } from '@app/utils/material.imports';
import { AppTranslateService } from '@app/utils/app-translate.service';
import { LanguageBase as Language } from '@core_models/LanguageBase';
import { TranslateModule } from '@ngx-translate/core';
import { SummaryService, SummaryResponse } from '@app/services/summary.service';
import { IncomeVsExpenseChartComponent } from '@app/features/charts/components/income-vs-expense-chart/income-vs-expense-chart.component';
import { ExpenseChartComponent } from '@app/features/charts/components/expense-chart/expense-chart.component';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [
    ...MATERIAL_IMPORTS,
    CommonModule,
    TranslateModule,
    IncomeVsExpenseChartComponent,
    ExpenseChartComponent
  ],
  templateUrl: './home.component.html',
  styleUrl: './home.component.css'
})
export class HomeComponent implements OnInit {
  languages: Language[] = [
    { code: 'en', name: 'English', flag: '🇬🇧' },
    { code: 'es', name: 'Español', flag: '🇪🇸' }
  ];

  currentLanguage: string;
  summary: SummaryResponse | null = null;
  investmentTotal = 0;
  loading = true;
  error = '';

  constructor(
    private translateService: AppTranslateService,
    private summaryService: SummaryService
  ) {
    this.currentLanguage = translateService.getCurrentLanguage();
  }

  ngOnInit(): void {
    // Filter only languages configured as available
    const availableLanguages = this.translateService.getAvailableLanguages();
    this.languages = this.languages.filter(lang =>
      availableLanguages.includes(lang.code)
    );

    this.loading = true;
    this.summaryService.getMonthSummary().subscribe({
      next: (res) => {
        this.summary = res.response;
        this.investmentTotal = (this.summary?.totals_over_time ?? [])
          .reduce((acc, t) => acc + (t.investment ?? 0), 0);
        this.loading = false;
      },
      error: () => {
        this.error = 'No se pudo cargar el resumen del mes.';
        this.loading = false;
      }
    });
  }

  changeLanguage(langCode: string): void {
    this.translateService.setLanguage(langCode);
    this.currentLanguage = langCode;
  }
}
