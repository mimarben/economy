import {
  Component,
  Input,
  Output,
  EventEmitter,
  AfterViewInit,
  OnChanges,
  OnDestroy,
  SimpleChanges,
  ViewChild,
} from '@angular/core';
import { CommonModule, DatePipe } from '@angular/common';
import { MatSort } from '@angular/material/sort';
import { MatPaginator } from '@angular/material/paginator';
import { MatTableDataSource } from '@angular/material/table';
import { FormsModule } from '@angular/forms';
import { TranslateModule } from '@ngx-translate/core';

import { ImportTransaction } from '@import_models/import-transaction.model';
import { ExpenseCategoryBase } from '@expenses_models/ExpenseCategoryBase';
import { IncomeCategoryBase } from '@incomes_models/IncomeCategoryBase';
import { AccountBase as Account } from '@finance_models/AccountBase';
import { SourceBase as Source } from '@finance_models/SourceBase';
import { ExcelParserService } from '@import_services/excel-parser.service';
import { UtilsService } from '@utils/utils.service';
import { MATERIAL_IMPORTS } from '@utils/material.imports';
import { SourceEnum } from '@app/core/const/Source.enum';

/**
 * Review table for the Excel import flow (exception-first workflow).
 *
 * Owns: state filters, search, bulk category, per-row edits
 * (category/source/user/account/ignore/selection) and pagination.
 * Mutates the transactions it receives in place; the parent component
 * reads them at import time.
 */
@Component({
  selector: 'app-import-preview',
  standalone: true,
  imports: [CommonModule, TranslateModule, ...MATERIAL_IMPORTS, FormsModule],
  // DatePipe is a @Pipe (not providedIn: 'root') — providing it here allows
  // the constructor injection used by activeFilterChips.
  providers: [DatePipe],
  templateUrl: './import-preview.component.html',
  styleUrl: './import-preview.component.scss',
})
export class ImportPreviewComponent implements AfterViewInit, OnChanges, OnDestroy {
  /** Parsed+categorized transactions (mutated in place by row edits). */
  @Input() transactions: ImportTransaction[] = [];
  @Input() expenseCategories: ExpenseCategoryBase[] = [];
  @Input() incomeCategories: IncomeCategoryBase[] = [];
  @Input() sources: Source[] = [];
  @Input() accounts: Account[] = [];
  @Input() users: any[] = [];

  /** Fired when the user presses the import button. */
  @Output() importClick = new EventEmitter<void>();

  @ViewChild(MatSort) sort!: MatSort;
  @ViewChild(MatPaginator) paginator!: MatPaginator;

  dataSource: MatTableDataSource<ImportTransaction> = new MatTableDataSource<ImportTransaction>([]);
  searchTerm = '';
  stateFilter: 'all' | 'nocat' | 'mismatch' | 'ignored' = 'all';
  bulkType: 'expense' | 'income' = 'expense';
  bulkCategoryId: number | null = null;
  displayedColumns = [
    'select',
    'date',
    'description',
    'type',
    'analysis',
    'amount',
    'balance',
    'category',
    'source',
    'user',
    'account',
  ];

  // ── Advanced filters (panel) ──
  advancedOpen = false;
  dateFrom: Date | null = null;
  dateTo: Date | null = null;
  amountMin: number | null = null;
  amountMax: number | null = null;
  typeFilter: 'all' | 'expense' | 'income' = 'all';
  accountFilterId: number | null = null;

  private searchTimer: ReturnType<typeof setTimeout> | null = null;

  constructor(
    private excelParser: ExcelParserService,
    private utilsService: UtilsService,
    private datePipe: DatePipe,
  ) {}

  ngAfterViewInit(): void {
    this.dataSource.sort = this.sort;
    if (this.paginator) {
      this.dataSource.paginator = this.paginator;
    }
  }

  ngOnChanges(changes: SimpleChanges): void {
    // New file loaded in the parent: reset review state. Guarded so async
    // inputs (categories, accounts...) arriving later don't wipe user filters.
    if (!changes['transactions']) {
      return;
    }
    this.searchTerm = '';
    this.stateFilter = 'all';
    this.advancedOpen = false;
    this.resetAdvancedFilters();
    this.updateDataSource();
  }

  ngOnDestroy(): void {
    if (this.searchTimer) {
      clearTimeout(this.searchTimer);
    }
  }

  // ── Exception counters ──

  get nocatCount(): number {
    return this.transactions.filter((t) => !t.suggestedCategoryId).length;
  }

  get mismatchCount(): number {
    return this.transactions.filter((t) => t.balanceMismatch).length;
  }

  get ignoredCount(): number {
    return this.transactions.filter((t) => t.ignore_in_analysis).length;
  }

  get selectedCount(): number {
    return this.transactions.filter((t) => t.selected).length;
  }

  // ── Filters / search ──

  setStateFilter(state: 'all' | 'nocat' | 'mismatch' | 'ignored'): void {
    this.stateFilter = state;
    this.updateDataSource();
  }

  applySearch(term: string): void {
    this.searchTerm = term;
    this.updateDataSource();
  }

  /** Debounced search: avoids refiltering the table on every keystroke. */
  applySearchDebounced(term: string): void {
    if (this.searchTimer) {
      clearTimeout(this.searchTimer);
    }
    this.searchTimer = setTimeout(() => {
      this.searchTimer = null;
      this.applySearch(term);
    }, 250);
  }

  clearSearch(): void {
    if (this.searchTimer) {
      clearTimeout(this.searchTimer);
      this.searchTimer = null;
    }
    this.applySearch('');
  }

  private filteredTransactions(): ImportTransaction[] {
    let rows = this.transactions;
    if (this.stateFilter === 'nocat') {
      rows = rows.filter((t) => !t.suggestedCategoryId);
    } else if (this.stateFilter === 'mismatch') {
      rows = rows.filter((t) => t.balanceMismatch);
    } else if (this.stateFilter === 'ignored') {
      rows = rows.filter((t) => t.ignore_in_analysis);
    }
    // Advanced filters (panel)
    if (this.typeFilter === 'expense') {
      rows = rows.filter((t) => t.amount < 0);
    } else if (this.typeFilter === 'income') {
      rows = rows.filter((t) => t.amount >= 0);
    }
    if (this.dateFrom) {
      const from = this.dateFrom.getTime();
      rows = rows.filter((t) => new Date(t.date).getTime() >= from);
    }
    if (this.dateTo) {
      const to = this.endOfDay(this.dateTo);
      rows = rows.filter((t) => new Date(t.date).getTime() <= to);
    }
    if (this.amountMin !== null && this.amountMin !== undefined) {
      rows = rows.filter((t) => t.amount >= (this.amountMin as number));
    }
    if (this.amountMax !== null && this.amountMax !== undefined) {
      rows = rows.filter((t) => t.amount <= (this.amountMax as number));
    }
    if (this.accountFilterId !== null) {
      rows = rows.filter((t) => t.account_id === this.accountFilterId);
    }
    if (this.searchTerm.trim()) {
      const needle = this.utilsService.normalize(this.searchTerm.trim());
      if (needle) {
        rows = rows.filter((t) =>
          this.utilsService.normalize(String(t.description ?? '')).includes(needle)
        );
      }
    }
    return rows;
  }

  private endOfDay(date: Date): number {
    const copy = new Date(date.getTime());
    copy.setHours(23, 59, 59, 999);
    return copy.getTime();
  }

  // ── Active filter chips ──

  /** Rows currently visible after all filters (dataSource holds them all). */
  get visibleCount(): number {
    return this.dataSource.data.length;
  }

  get advancedFilterCount(): number {
    let count = 0;
    if (this.typeFilter !== 'all') count++;
    if (this.dateFrom) count++;
    if (this.dateTo) count++;
    if (this.amountMin !== null && this.amountMin !== undefined) count++;
    if (this.amountMax !== null && this.amountMax !== undefined) count++;
    if (this.accountFilterId !== null) count++;
    return count;
  }

  get activeFilterChips(): { label: string; clear: () => void }[] {
    const chips: { label: string; clear: () => void }[] = [];
    const remove = (clear: () => void) => () => {
      clear();
      this.updateDataSource();
    };
    if (this.typeFilter !== 'all') {
      chips.push({
        label: this.typeFilter === 'expense' ? 'Gastos' : 'Ingresos',
        clear: remove(() => (this.typeFilter = 'all')),
      });
    }
    if (this.dateFrom) {
      chips.push({
        label: `Desde ${this.datePipe.transform(this.dateFrom, 'dd/MM/yyyy')}`,
        clear: remove(() => (this.dateFrom = null)),
      });
    }
    if (this.dateTo) {
      chips.push({
        label: `Hasta ${this.datePipe.transform(this.dateTo, 'dd/MM/yyyy')}`,
        clear: remove(() => (this.dateTo = null)),
      });
    }
    if (this.amountMin !== null && this.amountMin !== undefined) {
      chips.push({
        label: `≥ ${this.amountMin} €`,
        clear: remove(() => (this.amountMin = null)),
      });
    }
    if (this.amountMax !== null && this.amountMax !== undefined) {
      chips.push({
        label: `≤ ${this.amountMax} €`,
        clear: remove(() => (this.amountMax = null)),
      });
    }
    if (this.accountFilterId !== null) {
      const account = this.accounts.find((a) => a.id === this.accountFilterId);
      chips.push({
        label: account ? `Cuenta: ${account.name}` : 'Cuenta',
        clear: remove(() => (this.accountFilterId = null)),
      });
    }
    const term = this.searchTerm.trim();
    if (term) {
      chips.push({
        label: `"${term}"`,
        clear: remove(() => (this.searchTerm = '')),
      });
    }
    return chips;
  }

  private resetAdvancedFilters(): void {
    this.dateFrom = null;
    this.dateTo = null;
    this.amountMin = null;
    this.amountMax = null;
    this.typeFilter = 'all';
    this.accountFilterId = null;
  }

  clearAllFilters(): void {
    this.clearSearch();
    this.stateFilter = 'all';
    this.resetAdvancedFilters();
    this.updateDataSource();
  }

  // ── Bulk category ──

  applyBulkCategory(): void {
    if (!this.bulkCategoryId) {
      return;
    }
    const targets = this.transactions.filter(
      (t) =>
        t.selected &&
        !t.ignore_in_analysis &&
        (this.bulkType === 'expense' ? t.amount < 0 : t.amount >= 0)
    );
    for (const t of targets) {
      t.suggestedCategoryId = this.bulkCategoryId;
      this.suggestSourceForTransaction(t, this.bulkCategoryId);
    }
    this.updateDataSource();
  }

  // ── Row edits ──

  getCategories(t: ImportTransaction) {
    if (this.excelParser.inferTransactionType(t.amount) === 'expense') {
      return this.expenseCategories;
    }
    return this.incomeCategories;
  }

  onCategoryChange(transaction: ImportTransaction, categoryId: number) {
    transaction.suggestedCategoryId = categoryId;
    this.suggestSourceForTransaction(transaction, categoryId);
  }

  onAnalyzableChange(transaction: ImportTransaction, isAnalyzable: boolean): void {
    transaction.ignore_in_analysis = !isAnalyzable;
    transaction.selected = isAnalyzable;
    this.updateDataSource();
  }

  // ── Selection ──

  updateDataSource(): void {
    // Consistency: ignored rows can never be selected.
    this.transactions.forEach((t) => {
      if (t.ignore_in_analysis === true && t.selected === true) {
        t.selected = false;
      }
    });
    this.dataSource.data = this.filteredTransactions();
    if (this.sort) {
      this.dataSource.sort = this.sort;
    }
    if (this.paginator) {
      this.dataSource.paginator = this.paginator;
    }
  }

  toggleAll(checked: boolean) {
    this.transactions.forEach((t) => {
      t.selected = t.ignore_in_analysis === true ? false : checked;
    });
    this.updateDataSource();
  }

  isAllSelected(): boolean {
    return this.transactions.length > 0 && this.transactions.every((t) => t.selected);
  }

  isSomeSelected(): boolean {
    const selectedCount = this.transactions.filter((t) => t.selected).length;
    return selectedCount > 0 && selectedCount < this.transactions.length;
  }

  // ── Source suggestion (merchant name heuristic, no HTTP) ──

  private suggestSourceForTransaction(transaction: ImportTransaction, categoryId: number) {
    if (!categoryId) {
      transaction.suggestedSourceId = null;
      return;
    }
    const sourceByDescription = this.findSourceByDescription(transaction);
    if (sourceByDescription?.id) {
      transaction.suggestedSourceId = sourceByDescription.id;
      transaction.source_id = sourceByDescription.id;
      this.updateDataSource();
      return;
    }
    // Sin match por descripción: se deja null. El backend asigna el source
    // con sus source_rules al importar.
  }

  private findSourceByDescription(transaction: ImportTransaction): Source | null {
    const description = this.utilsService.normalize(String(transaction.description ?? ''));
    if (!description) return null;
    const expectedType: SourceEnum = transaction.amount < 0 ? SourceEnum.EXPENSE : SourceEnum.INCOME;
    const candidates = this.sources.filter((s) => s.type === expectedType);
    if (!candidates.length) return null;

    const sortedByNameLength = [...candidates].sort(
      (a, b) => (b.name?.length ?? 0) - (a.name?.length ?? 0)
    );

    return (
      sortedByNameLength.find((source) => {
        const sourceName = this.utilsService.normalize(String(source.name ?? ''));
        return !!sourceName && description.includes(sourceName);
      }) ?? null
    );
  }
}
