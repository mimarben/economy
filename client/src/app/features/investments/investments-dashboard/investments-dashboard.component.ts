import { Component, OnInit, computed, inject, signal, effect, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { TranslateModule } from '@ngx-translate/core';
import { MATERIAL_IMPORTS } from '@app/utils/material.imports';
import { MatTableModule, MatTableDataSource } from '@angular/material/table';
import { MatPaginator, MatPaginatorModule } from '@angular/material/paginator';
import { MatSort, MatSortModule, Sort } from '@angular/material/sort';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatChipsModule } from '@angular/material/chips';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatSnackBar } from '@angular/material/snack-bar';
import { ApiResponse } from '@app/models/core/APIResponse';
import {
  DashboardEntry,
  InvestmentsDashboard,
  AssetClass,
  PositionStatus,
  InstrumentSearchResult,
  SearchResponse,
  UnquotedEntry
} from '@investments_models/MarketQuotes';
import { MarketQuoteService } from '@investments_services/market-quote.service';

// Colores por categoría definidos una vez como tokens y reutilizados en tabla, filtros, badges y gráficos
export const CATEGORY_COLORS: Record<AssetClass, { background: string; color: string; border: string }> = {
  ETF: { background: '#E3F2FD', color: '#1565C0', border: '#90CAF9' },
  FUND: { background: '#E8F5E9', color: '#2E7D32', border: '#A5D6A7' },
  STOCK: { background: '#FFF3E0', color: '#EF6C00', border: '#FFCC80' },
  CRYPTO: { background: '#F3E5F5', color: '#7B1FA2', border: '#CE93D8' },
  BOND: { background: '#E0E0E0', color: '#424242', border: '#BDBDBD' },
  MANAGED_PORTFOLIO: { background: '#F5F5F5', color: '#757575', border: '#E0E0E0' },
  OTHER: { background: '#FAFAFA', color: '#9E9E9E', border: '#BDBDBD' }
};

export const ALL_ASSET_CLASSES: AssetClass[] = ['ETF', 'FUND', 'STOCK', 'CRYPTO', 'BOND', 'MANAGED_PORTFOLIO', 'OTHER'];

@Component({
  selector: 'app-investments-dashboard',
  standalone: true,
  imports: [
    ...MATERIAL_IMPORTS,
    CommonModule,
    TranslateModule,
    MatTableModule,
    MatPaginatorModule,
    MatSortModule,
    MatInputModule,
    MatSelectModule,
    MatFormFieldModule,
    MatChipsModule,
    MatTooltipModule,
    MatIconModule,
    MatButtonModule
  ],
  templateUrl: './investments-dashboard.component.html',
  styleUrl: './investments-dashboard.component.css'
})
export class InvestmentsDashboardComponent implements OnInit {
  private marketQuoteService = inject(MarketQuoteService);
  private snackBar = inject<MatSnackBar | null>(MatSnackBar);

  readonly displayedColumns = [
    'category', 'name', 'units', 'price', 'currency', 'market_value', 
    'cost', 'pl', 'quote_info', 'status'
  ];

  ALL_ASSET_CLASSES = ALL_ASSET_CLASSES;

  dashboard = signal<InvestmentsDashboard | null>(null);
  isLoading = signal(false);
  isRefreshing = signal(false);
  errorMessage = signal('');

  // Filtros y búsqueda
  searchQuery = signal('');
  selectedCategory = signal<AssetClass | 'ALL' | null>('ALL');
  selectedStatus = signal<PositionStatus | 'ALL' | null>('ALL');
  showClosedPositions = signal(false);

  // Filtro computed para decidir qué vista mostrar
  showHistoricalView = computed(() => this.showClosedPositions());

  entries = computed<DashboardEntry[]>(() => this.dashboard()?.entries ?? []);

  // Posiciones sin ISIN (carteras gestionadas, cripto): valoración manual
  unquotedEntries = computed<UnquotedEntry[]>(() => this.dashboard()?.unquoted_entries ?? []);
  hasUnquoted = computed(() => this.unquotedEntries().length > 0);

  readonly unquotedColumns = ['name', 'units', 'value', 'cost', 'pl', 'currency', 'updated'];

  /** Valor total = valor de mercado (donde hay cotización) + valoración manual del resto. */
  totalValuedValue = computed<number | null>(() => {
    const data = this.dashboard();
    if (!data) return null;
    const market = data.total_market_value ?? null;
    const reported = data.total_reported_value ?? null;
    if (market === null && reported === null) return null;
    return (market ?? 0) + (reported ?? 0);
  });

  /** P/L total = P/L de mercado + P/L de valoraciones manuales. */
  totalValuedPl = computed<number | null>(() => {
    const data = this.dashboard();
    if (!data) return null;
    const market = data.total_unrealized_pl ?? null;
    const reported = data.total_reported_pl ?? null;
    if (market === null && reported === null) return null;
    return (market ?? 0) + (reported ?? 0);
  });

  totalPositions = computed(() => this.entries().length + this.unquotedEntries().length);

  // DataSource para la tabla con paginación y ordenación
  dataSource = signal<MatTableDataSource<DashboardEntry>>(new MatTableDataSource<DashboardEntry>([]));

  // Computed para entradas filtradas
  filteredEntries = computed<DashboardEntry[]>(() => {
    let filtered = this.entries();

    // Aplicar búsqueda por texto
    const query = this.searchQuery().toLowerCase();
    if (query) {
      filtered = filtered.filter(entry => {
        const name = (entry.name || '').toLowerCase();
        const isin = (entry.isin || '').toLowerCase();
        const symbol = (entry.symbol || '').toLowerCase();
        const category = (entry.category || '').toLowerCase();
        const assetClass = (entry.asset_class || '').toLowerCase();
        return name.includes(query) || isin.includes(query) || symbol.includes(query) || 
               category.includes(query) || assetClass.includes(query);
      });
    }

    // Aplicar filtro por categoría
    const category = this.selectedCategory();
    if (category && category !== 'ALL') {
      filtered = filtered.filter(entry => entry.category === category || entry.asset_class === category);
    }

    // Aplicar filtro por estado
    const status = this.selectedStatus();
    if (status && status !== 'ALL') {
      filtered = filtered.filter(entry => entry.position_status === status);
    }

    // Si no está mostrando histórico, ocultar cerradas
    if (!this.showClosedPositions()) {
      filtered = filtered.filter(entry => entry.position_status !== 'CLOSED');
    }

    return filtered;
  });

  // Effect para actualizar el dataSource cuando cambia filteredEntries
  private updateEffect = effect(() => {
    // No actualizar si estamos cargando
    if (this.isLoading()) {
      return;
    }
    const entries = this.filteredEntries();
    const dataSource = new MatTableDataSource<DashboardEntry>(entries);
    this.dataSource.set(dataSource);
  });

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
        // El effect se encarga de actualizar el dataSource automáticamente
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

  // Método para mostrar un mensaje en el snack bar
  showSnackbar(message: string, action: string = 'Cerrar'): void {
    this.snackBar?.open(message, action, {
      duration: 3000,
      horizontalPosition: 'center',
      verticalPosition: 'bottom',
    });
  }

  displayName(entry: DashboardEntry): string {
    return entry.name || entry.symbol || entry.isin;
  }

  // Obtener categoría real (prioridad a asset_class si no hay category)
  getCategory(entry: DashboardEntry): AssetClass | null {
    return entry.category || entry.asset_class || null;
  }

  // Obtener color por categoría
  getCategoryColor(category: AssetClass | null): { background: string; color: string; border: string } {
    if (!category) {
      return CATEGORY_COLORS.OTHER;
    }
    return CATEGORY_COLORS[category] || CATEGORY_COLORS.OTHER;
  }

  // Obtener etiqueta de categoría
  getCategoryLabel(category: AssetClass | null): string {
    if (!category) {
      return 'OTRO';
    }
    const labels: Record<AssetClass, string> = {
      ETF: 'ETF',
      FUND: 'FONDO',
      STOCK: 'ACCIONES',
      CRYPTO: 'CRYPTO',
      BOND: 'BONO',
      MANAGED_PORTFOLIO: 'CARTERA GESTIONADA',
      OTHER: 'OTRO'
    };
    return labels[category] || category;
  }

  // Formatear moneda con el símbolo correcto
  formatCurrency(value: number | null | undefined, currency: string | null | undefined): string {
    if (value === null || value === undefined) {
      return '—';
    }
    // Usar el símbolo real de la moneda
    try {
      const formatter = new Intl.NumberFormat('es-ES', {
        style: 'currency',
        currency: currency || 'EUR',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      });
      return formatter.format(value);
    } catch {
      // Fallback si la moneda no es válida
      const symbol = currency === 'EUR' ? '€' : currency || '';
      return `${value.toFixed(2)} ${symbol}`;
    }
  }

  formatPercentage(value: number | null | undefined): string {
    if (value === null || value === undefined) {
      return '—';
    }
    return `${value.toFixed(2)}%`;
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

  @ViewChild(MatSort) sort!: MatSort;
  @ViewChild(MatPaginator) paginator!: MatPaginator;

  // Búsqueda universal
  searchInstruments(query: string): void {
    if (!query.trim()) {
      return;
    }

    this.marketQuoteService.searchInstruments(query).subscribe({
      next: (response: ApiResponse<SearchResponse>) => {
        if (response.response.results.length === 0) {
          this.showSnackbar('No se encontraron resultados para tu búsqueda');
          return;
        }

        if (response.response.results.length === 1) {
          // Auto-seleccionar si hay un solo resultado
          this.selectSearchResult(response.response.results[0]);
        } else {
          // Mostrar dialog de selección cuando hay varios resultados
          this.showSelectionDialog(response.response.results);
        }
      },
      error: () => {
        this.showSnackbar('Error al realizar la búsqueda');
      }
    });
  }

  onSearchInput(event: Event): void {
    const value = (event.target as HTMLInputElement).value;
    this.searchQuery.set(value);
  }

  clearSearch(): void {
    this.searchQuery.set('');
  }

  selectSearchResult(result: InstrumentSearchResult): void {
    // Aquí se implementará la lógica de selección de instrumento para crear/actualizar aportación
    // Por ahora, solo mostramos un mensaje
    this.showSnackbar(`Instrumento seleccionado: ${result.name} (${result.isin || result.symbol})`);
    // En la implementación completa, abriríamos un modal para elegir acción:
    // - Crear nueva aportación
    // - Enlazar con aportación existente
    // - Ver detalle del instrumento
  }

  showSelectionDialog(results: InstrumentSearchResult[]): void {
    // Implementación pendiente: mostrar dialog de selección cuando hay varios resultados
    this.showSnackbar(`Selecciona uno de los ${results.length} resultados encontrados`);
  }

  // Navegar al detalle del instrumento
  navigateToInstrumentDetail(isin: string): void {
    // Implementación pendiente: navegar a una vista de detalle
    this.showSnackbar(`Ver detalle de ${isin}`);
  }

  // Toggle para mostrar posiciones cerradas
  toggleShowClosedPositions(): void {
    this.showClosedPositions.set(!this.showClosedPositions());
  }

  // Manejar cambio de categoría
  onCategoryChange(value: AssetClass | 'ALL' | null): void {
    this.selectedCategory.set(value);
  }

  // Manejar cambio de estado
  onStatusChange(value: PositionStatus | 'ALL' | null): void {
    this.selectedStatus.set(value);
  }

  // Computed para saber si hay entradas
  hasEntries = computed(() => this.filteredEntries().length > 0);
}
