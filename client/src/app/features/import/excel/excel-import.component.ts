import { Component, OnInit, DestroyRef, inject } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { CommonModule } from '@angular/common';
import { firstValueFrom } from 'rxjs';
import * as XLSX from 'xlsx';

import { ExpenseCategoryBase } from '@expenses_models/ExpenseCategoryBase';
import { AccountBase as Account } from '@finance_models/AccountBase';
import { SourceBase as Source } from '@finance_models/SourceBase';
import { CardBase as Card } from '@cards_models/CardBase';
import { AccountService } from '@finance_services/account.service';
import { SourceService } from '@finance_services/source.service';
import { ExpenseCategoryService } from '@app/services/expenses/expense-category.service';
import { IncomeCategoryBase } from '@incomes_models/IncomeCategoryBase';
import { IncomeCategoryService } from '@incomes_services/income-category.service';
import { UtilsService } from '@utils/utils.service';
import { RuleCategorizerService } from '@import_services/rule-categorizer.service';
import { ExcelParserService } from '@import_services/excel-parser.service';
import { ToastService } from '@core_services/toast.service';
import { TransactionImportService } from '@app/services/import/transaction-import.service';
import { CardService } from '@app/services/cards/cards.service';
import { ImportProfilesService, ImportOriginsService } from '@import_services/import-profiles.service';
import { BankService } from '@finance_services/bank.service';
import { BankBase as Bank } from '@finance_models/BankBase';
import { AuthService } from '@app/services/auth/auth.service';
import { UserService } from '@app/services/users/user.service';
import { CategoryRuleService } from '@app/services/rules/category-rule.service';

import { ImportTransaction } from '@import_models/import-transaction.model';
import { ImportOriginBase as ImportOrigin } from '@app/models/import/import-originBase';
import { ImportProfileBase as ImportProfile } from '@app/models/import/import-profileBase';
import { ImportPreviewComponent } from '../preview/import-preview/import-preview.component';

import { AppTranslateService } from '@utils/app-translate.service';
import { TranslateModule } from '@ngx-translate/core';
import { MATERIAL_IMPORTS } from '@utils/material.imports';
import { FormsModule } from '@angular/forms';
import { CurrencyEnum } from '@app/core/const/Currency.enum';

/**
 * Excel import screen (parent): destination selection (origin/profile →
 * bank/account/card/user), file parsing, titular detection and backend
 * categorization. The review table lives in ImportPreviewComponent.
 */
@Component({
  selector: 'app-excel-import',
  standalone: true,
  imports: [CommonModule, TranslateModule, ...MATERIAL_IMPORTS, FormsModule, ImportPreviewComponent],
  templateUrl: './excel-import.component.html',
  styleUrl: './excel-import.component.scss',
})
export class ExcelImportComponent implements OnInit {
  banks: Bank[] = [];
  accounts: Account[] = [];
  filteredAccounts: Account[] = [];
  sources: Source[] = [];
  cards: Card[] = [];
  selectedCard: Card | null = null;
  importOrigins: ImportOrigin[] = [];
  importProfiles: ImportProfile[] = [];
  filteredProfiles: ImportProfile[] = [];
  selectedOrigin: ImportOrigin | null = null;
  users: any[] = [];
  accountUsers: any[] = [];
  selectedUserId: number | null = null;

  selectedBank: Bank | null = null;

  selectedAccount: Account | null = null;

  selectedProfile: ImportProfile | null = null;

  transactions: ImportTransaction[] = [];

  expenseCategories: ExpenseCategoryBase[] = [];
  incomeCategories: IncomeCategoryBase[] = [];
  isClassifying = false;

  private destroyRef = inject(DestroyRef);

  constructor(
    private bankService: BankService,
    private toastService: ToastService,
    private translateService: AppTranslateService,
    private incomeCategoryService: IncomeCategoryService,
    private expenseCategoryService: ExpenseCategoryService,
    private ruleCategorizerService: RuleCategorizerService,
    private excelParser: ExcelParserService,
    private utilsService: UtilsService,
    private transactionImportService: TransactionImportService,
    private accountService: AccountService,
    private sourceService: SourceService,
    private cardService: CardService,
    private importOriginsService: ImportOriginsService,
    private importProfilesService: ImportProfilesService,
    private authService: AuthService,
    private userService: UserService,
    private categoryRuleService: CategoryRuleService,
  ) { }
  ngOnInit(): void {
    this.bankService.getBanks().pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
      next: (res) => {
        this.banks = res.response;
      },
      error: (error) => {
        this.toastService.error(
          this.translateService.translateKey('ERROR_LOAD_BANKS'),
        );
      },
    });

    this.accountService.getAll().pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
      next: (res) => {
        this.accounts = res.response;
      },
      error: (error) => {
        this.toastService.error(
          this.translateService.translateKey('ERROR_LOAD_ACCOUNTS'),
        );
      },
    });

    this.sourceService.getAll().pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
      next: (res) => {
        this.sources = res.response;
      },
      error: (error) => {
        this.toastService.error(
          this.translateService.translateKey('ERROR_LOAD_SOURCES'),
        );
      },
    });

    this.userService.getUsers().pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
      next: (res) => {
        this.users = res.response ?? [];
      },
      error: () => {
        this.toastService.error('No se pudieron cargar los usuarios');
      },
    });

    this.incomeCategoryService.getAll().pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
      next: (res) => {
        this.incomeCategories = res.response;
      },
      error: (error) => {
        this.toastService.error(
          this.translateService.translateKey('ERROR_LOAD_INCOMES_CATEGORIES'),
        );
      },
    });
    this.expenseCategoryService.getAll().pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
      next: (res) => {
        this.expenseCategories = res.response;
      },
      error: (error) => {
        this.toastService.error(
          this.translateService.translateKey('ERROR_LOAD_EXPENSES_CATEGORIES'),
        );
      },
    });
    this.cardService.getAll().pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
      next: (res) => {
        this.cards = res.response;
      },
      error: (error) => {
        this.toastService.error(
          this.translateService.translateKey('ERROR_LOAD_CARDS'),
        );
      },
    });
    this.importOriginsService.getOrigins().pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
      next: (res) => {
        this.importOrigins = (res.response ?? []).filter((origin) => origin.active !== false);
      },
      error: () => {
        this.toastService.error('No se pudieron cargar los orígenes de importación');
      },
    });
    this.importProfilesService.getProfiles().pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
      next: (res) => {
        this.importProfiles = (res.response ?? []).filter((profile) => profile.active !== false);
      },
      error: () => {
        this.toastService.error('No se pudieron cargar los perfiles de importación');
      },
    });
  }

  // ── Destination selection ──

  onBankSelected(bankId: number) {
    const id = Number(bankId);
    const bank = this.banks.find((b) => b.id === id);
    if (!bank) {
      console.warn('Bank not found');
      this.toastService.success(
        this.translateService.translateKey('BANK.NOT_FOUND'),
      );
      return;
    }
    this.selectedBank = bank;
    this.filterAccountsByBank(bank.id);
    // Keep the selected card (and its account) when the bank still matches it
    // (e.g. the bank was auto-selected by the card and re-picked manually).
    if (this.selectedCard) {
      const cardAccount = this.accounts.find((a) => a.id === this.selectedCard!.account_id);
      if (cardAccount && cardAccount.bank_id === bank.id) {
        this.applyAccountSelection(cardAccount);
        return;
      }
      this.selectedCard = null;
    }
    this.selectedAccount = null;
  }

  onOriginSelected(originId: number | null) {
    const id = Number(originId);
    if (!originId || Number.isNaN(id)) {
      this.selectedOrigin = null;
      this.filteredProfiles = [];
      this.selectedProfile = null;
      return;
    }

    this.selectedOrigin = this.importOrigins.find((origin) => origin.id === id) ?? null;
    this.filteredProfiles = this.importProfiles.filter((profile) => profile.origin_id === id);
    this.selectedProfile = null;
  }

  onProfileSelected(profileId: number | null) {
    const id = Number(profileId);
    if (!profileId || Number.isNaN(id)) {
      this.selectedProfile = null;
      return;
    }
    this.selectedProfile = this.filteredProfiles.find((profile) => profile.id === id) ?? null;
  }

  onCardSelected(card: Card | null) {
    this.selectedCard = card;
    if (!card?.account_id) {
      return;
    }
    // A card knows its account (e.g. Pass cards settle into an ING account):
    // auto-select bank + account from the card so the user doesn't have to.
    const account = this.accounts.find((a) => a.id === card.account_id);
    if (!account) {
      console.warn('Card account not found', card.account_id);
      return;
    }
    this.selectedBank = this.banks.find((b) => b.id === account.bank_id) ?? null;
    this.filterAccountsByBank(account.bank_id);
    this.applyAccountSelection(account);
  }

  onAccountSelected(accountId: number) {
    const id = Number(accountId);
    const account = this.filteredAccounts.find((a) => a.id === id);
    if (!account) {
      console.warn('Account not found for selected bank');
      return;
    }
    // Keep the selected card only if it belongs to the chosen account.
    if (this.selectedCard && this.selectedCard.account_id !== account.id) {
      this.selectedCard = null;
    }
    this.applyAccountSelection(account);
  }

  private applyAccountSelection(account: Account) {
    this.selectedAccount = account;
    this.accountUsers = account.users || [];
    const currentUserId = this.authService.getUserId();
    const defaultUser =
      this.users.find((u) => u.id === currentUserId) ??
      this.accountUsers.find((u) => u.id === currentUserId) ??
      this.accountUsers[0] ??
      this.users.find((u) => !String(u.name ?? '').toLowerCase().startsWith('admin')) ??
      null;
    this.selectedUserId = defaultUser?.id ?? null;
    this.transactions.forEach((t) => {
      t.account_id = account.id;
      t.suggestedAccountId = account.id;
      t.user_id = this.selectedUserId;
    });
  }

  onUserSelected(userId: number | null) {
    this.selectedUserId = userId;
    this.transactions.forEach((t) => {
      t.user_id = userId;
    });
  }

  private filterAccountsByBank(bankId: number): void {
    this.filteredAccounts = this.accounts.filter((a) => a.bank_id === bankId);
  }

  /**
   * Match a holder name read from the file metadata against the users table
   * (accent-insensitive, either direction containment).
   */
  private matchUser(titular: string): any | null {
    const needle = this.utilsService.normalize(titular).replace(/\s+/g, ' ').trim();
    if (!needle) return null;
    return (
      this.users.find((u) => {
        const name = this.utilsService.normalize(String(u.name ?? '')).trim();
        const full = this.utilsService
          .normalize(`${u.name ?? ''} ${u.surname1 ?? ''} ${u.surname2 ?? ''}`)
          .replace(/\s+/g, ' ')
          .trim();
        return name.length > 2 && (needle.includes(name) || needle.includes(full) || full.includes(needle));
      }) ?? null
    );
  }

  // ── File parsing + categorization ──

  async onFileChange(event: Event) {
    if (!this.selectedProfile) {
      console.warn(
        'Import profile not found for bank',
        this.selectedBank?.name,
      );
      this.toastService.error(
        this.translateService.translateKey('BANK.PROFILE_NOT_FOUND'),
      );
      return;
    }

    const input = event.target as HTMLInputElement;

    if (!input.files?.length) return;

    const file = input.files[0];

    const reader = new FileReader();

    reader.onload = async (e: any) => {
      const workbook = XLSX.read(e.target.result, {
        type: 'binary',
      });

      const sheetName = workbook.SheetNames[0];
      const sheet = workbook.Sheets[sheetName];

      const rows: any[][] = XLSX.utils.sheet_to_json(sheet, {
        header: 1,
        raw: false,
      });

      const parsed = this.excelParser.parse(rows, this.selectedProfile!, {
        selectedAccount: this.selectedAccount,
        selectedCard: this.selectedCard,
        selectedUserId: this.selectedUserId,
      });

      if (!parsed) {
        console.error('Column detection failed', this.excelHeaders);
        this.toastService.error('Excel format not recognized');
        return;
      }

      const tempTransactions: ImportTransaction[] = parsed.transactions;
      const droppedRows = parsed.dataRows.length - tempTransactions.length;
      if (droppedRows > 0) {
        this.toastService.warning(
          `${droppedRows} filas sin importe válido fueron descartadas del fichero.`
        );
      }

      // Titular detection: match the holder name from the file metadata
      // (e.g. Pass row 3 "Nombre Apellidos") against the users table and
      // preselect it for every row.
      if (parsed.titularName) {
        const titularUser = this.matchUser(parsed.titularName);
        if (titularUser?.id) {
          this.selectedUserId = titularUser.id;
          tempTransactions.forEach((t) => (t.user_id = titularUser.id));
          this.toastService.success(
            `Titular detectado en el fichero: ${titularUser.name} ${titularUser.surname1 ?? ''}`.trim()
          );
        } else {
          this.toastService.warning(
            `Titular del fichero "${parsed.titularName}" no coincide con ningún usuario: revísalo.`
          );
        }
      }

      // Categorize with the SAME backend engine the import uses
      // (category rules + source rules + ignore flag in one pass), so the
      // preview shows exactly what will be stored. Local rules remain as
      // fallback if the endpoint is unavailable.
      const categorized = await this.categorizeTransactions(tempTransactions);
      const uncategorized = categorized.filter(t => !t.suggestedCategoryId);
      if (uncategorized.length > 0) {
        this.toastService.warning(
          `${uncategorized.length} transacciones sin categoría: revísalas antes de importar.`
        );
      }

      // Reconciliation: flag rows that break the statement's balance chain.
      const mismatches = this.validateBalanceChain(categorized);
      if (mismatches > 0) {
        this.toastService.warning(
          `${mismatches} filas no cuadran con el saldo del extracto (ver filtro "Saldo ✗").`
        );
      }

      this.transactions = categorized;
      this.isClassifying = false;
    };

    reader.readAsBinaryString(file);
  }

  excelHeaders: string[] = [];
  excelRows: any[] = [];

  /**
   * Categorize parsed transactions via the backend batch endpoint
   * (same rule engine as the import: category + source + ignore flag).
   * Falls back to the local rule cache when the endpoint fails.
   */
  private async categorizeTransactions(temp: ImportTransaction[]): Promise<ImportTransaction[]> {
    const items = temp.map((t) => ({
      description: String(t.description ?? ''),
      type: t.amount < 0 ? ('expense' as const) : ('income' as const),
    }));
    try {
      const results = await firstValueFrom(this.categoryRuleService.categorizeBatch(items));
      temp.forEach((t, i) => {
        const r = results[i];
        if (!r) return;
        t.suggestedCategoryId = r.category_id ?? null;
        const match = (t.amount < 0 ? this.expenseCategories : this.incomeCategories)
          .find((c) => c.id === r.category_id);
        t.suggestedCategoryName = match?.name ?? null;
        if (r.source_id) {
          t.suggestedSourceId = r.source_id;
          t.source_id = r.source_id;
        }
        t.ignore_in_analysis = !!r.ignore_in_analysis;
        if (t.ignore_in_analysis) {
          t.selected = false;
        }
      });
      return temp;
    } catch (err) {
      console.warn('Backend categorization unavailable, using local rules', err);
      await this.ruleCategorizerService.refreshRules();
      return this.ruleCategorizerService.categorize(
        temp,
        this.incomeCategories,
        this.expenseCategories,
      );
    }
  }

  /**
   * Reconciliation check on the statement's running balance:
   * balance[i] must equal balance[i-1] + amount[i]. Rows breaking the
   * chain are flagged (balanceMismatch) for review instead of failing silently.
   */
  private validateBalanceChain(transactions: ImportTransaction[]): number {
    let mismatches = 0;
    let previous: number | null = null;
    for (const t of transactions) {
      const balance =
        t.balance === null || t.balance === undefined || isNaN(Number(t.balance))
          ? null
          : Number(t.balance);
      if (balance === null) {
        continue; // statement without a usable balance column
      }
      if (previous !== null) {
        const expected = previous + Number(t.amount);
        if (Math.abs(expected - balance) > 0.005) {
          t.balanceMismatch = true;
          mismatches++;
        }
      }
      previous = balance;
    }
    return mismatches;
  }

  // ── Import ──

  confirmImport() {
    // Only process transactions marked as importable (selected: true)
    const importable = this.transactions.filter((t) => t.selected);
    if (!importable.length) {
      this.toastService.warning('No hay transacciones marcadas para importar');
      return;
    }

    // Only include transactions that have a category assigned
    const validTransactions = importable.filter((t) => t.suggestedCategoryId);
    const excludedNoCategory = importable.length - validTransactions.length;
    if (!validTransactions.length) {
      this.toastService.warning('Las transacciones marcadas no tienen categoría asignada');
      return;
    }

    const expenses = validTransactions.filter((t) => t.amount < 0);
    const incomes = validTransactions.filter((t) => t.amount >= 0);

    const expensesDraftPayload = expenses.map((t) => ({
      name: String(t.description).trim().slice(0, 255),
      description: String(t.description).trim(),
      amount: Math.abs(Number(t.amount)),
      date: t.date,
      category_id: t.suggestedCategoryId,
      source_id: t.source_id ?? t.suggestedSourceId,
      account_id: t.account_id ?? this.selectedAccount?.id,
      card_id: t.card_id ?? this.selectedCard?.id ?? null,
      ignore_in_analysis: t.ignore_in_analysis ?? false,
      currency: CurrencyEnum.EUR,
      user_id: t.user_id ?? this.selectedUserId,
    }));

    const incomesDraftPayload = incomes.map((t) => ({
      name: String(t.description).trim().slice(0, 255),
      description: String(t.description).trim(),
      amount: Number(t.amount),
      date: t.date,
      category_id: t.suggestedCategoryId,
      source_id: t.source_id ?? t.suggestedSourceId,
      account_id: t.account_id ?? this.selectedAccount?.id,
      ignore_in_analysis: t.ignore_in_analysis ?? false,
      currency: CurrencyEnum.EUR,
      user_id: t.user_id ?? this.selectedUserId,
    }));

    const payload = {
      expenses: expensesDraftPayload,
      incomes: incomesDraftPayload
    };

    this.transactionImportService.importAtomic(payload).pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
      next: (res) => {
        const inserted = res.response?.inserted ?? (res.response?.expenses_created ?? 0) + (res.response?.incomes_created ?? 0);
        const duplicates = res.response?.duplicates ?? 0;

        if (excludedNoCategory > 0) {
          this.toastService.warning(
            `Importadas ${inserted}, duplicados ${duplicates}. ATENCIÓN: ${excludedNoCategory} filas quedaron SIN importar por no tener categoría.`
          );
        } else {
          this.toastService.success(
            `¡Éxito! ${inserted} transacciones importadas. ${duplicates} duplicados ignorados.`
          );
        }
        this.transactions = [];
        this.excelRows = [];
      },
      error: (err) => {
        console.error('Error importing atomic transactions:', err);
        this.toastService.error('Error durante la importación. Ningún dato fue guardado.');
      }
    });
  }
}
