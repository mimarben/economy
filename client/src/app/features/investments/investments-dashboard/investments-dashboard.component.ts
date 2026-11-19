import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { TranslateModule } from '@ngx-translate/core';
import { MATERIAL_IMPORTS } from '@app/utils/material.imports';
import { ApiResponse } from '@app/models/core/APIResponse';
import { DashboardEntry, InvestmentsDashboard } from '@investments_models/MarketQuotes';
import { MarketQuoteService } from '@investments_services/market-quote.service';

@Component({
  selector: 'app-investments-dashboard',
  standalone: true,
  imports: [...MATERIAL_IMPORTS, CommonModule, TranslateModule],
  templateUrl: './investments-dashboard.component.html',
  styleUrl: './investments-dashboard.component.css'
})
export class InvestmentsDashboardComponent implements OnInit {
  private marketQuoteService = inject(MarketQuoteService);

  readonly displayedColumns = [
    'name', 'instrument_type', 'units', 'total_contributed',
    'last_price', 'change_pct', 'market_value', 'unrealized_pl', 'quote_status',
  ];

  dashboard = signal<InvestmentsDashboard | null>(null);
  isLoading = signal(false);
  isRefreshing = signal(false);
  errorMessage = signal('');

  entries = computed<DashboardEntry[]>(() => this.dashboard()?.entries ?? []);
  hasEntries = computed(() => this.entries().length > 0);

  ngOnInit(): void {
    this.load();
  }

  load(forceRefresh = false): void {
    if (forceRefresh) {
      this.isRefreshing.set(true);
    } else {
      this.isLoading.set(true);
    }
    this.errorMessage.set('');

    this.marketQuoteService.getDashboard(forceRefresh).subscribe({
      next: (response: ApiResponse<InvestmentsDashboard>) => {
        this.dashboard.set(response.response);
        this.isLoading.set(false);
        this.isRefreshing.set(false);
      },
      error: () => {
        this.errorMessage.set('Error loading market dashboard');
        this.isLoading.set(false);
        this.isRefreshing.set(false);
      },
    });
  }

  refresh(): void {
    this.load(true);
  }

  displayName(entry: DashboardEntry): string {
    return entry.name || entry.symbol || entry.isin;
  }

  changeClass(pct: number | null | undefined): string {
    if (pct === null || pct === undefined) return 'change-flat';
    if (pct > 0) return 'change-up';
    if (pct < 0) return 'change-down';
    return 'change-flat';
  }

  changeIcon(pct: number | null | undefined): string {
    if (pct === null || pct === undefined) return 'remove';
    if (pct > 0) return 'arrow_drop_up';
    if (pct < 0) return 'arrow_drop_down';
    return 'remove';
  }

  /** Tooltip hint for partially-known units (some contributions unlogged). */
  unitsTooltip(entry: DashboardEntry): string {
    return entry.units_partial
      ? 'Algunas aportaciones de este ISIN no tienen registro de unidades: el total puede estar incompleto'
      : '';
  }
}
