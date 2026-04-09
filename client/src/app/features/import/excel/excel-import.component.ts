import { Component, OnInit, AfterViewInit, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatSort } from '@angular/material/sort';
import { MatTableDataSource } from '@angular/material/table';
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
import { TransactionAiService } from '@services/ai/transaction-ai.service';
import { RuleCategorizerService } from '@import_services/rule-categorizer.service';
import { ToastService } from '@core_services/toast.service';
import { TransactionImportService } from '@app/services/import/transaction-import.service';
import { CardService } from '@app/services/cards/cards.service';
import { ImportProfilesService, ImportOriginsService } from '@import_services/import-profiles.service';
import { BankService } from '@finance_services/bank.service';
import { BankBase as Bank } from '@finance_models/BankBase';
import { ImportTransaction } from '@import_models/import-transaction.model';
import { ClassifyRequest, ClassifyResult, ClassifyPayload } from '@import_models/classify-request-ai';
import { ImportOriginBase as ImportOrigin } from '@app/models/import/import-originBase';
import { ImportProfileBase as ImportProfile } from '@app/models/import/import-profileBase';

import { AppTranslateService } from '@utils/app-translate.service';
import { TranslateModule } from '@ngx-translate/core';
import { MATERIAL_IMPORTS } from '@utils/material.imports';
import { FormsModule } from '@angular/forms';
@Component({
  selector: 'app-excel-import',
  standalone: true,
  imports: [CommonModule, TranslateModule, ...MATERIAL_IMPORTS, FormsModule],
  templateUrl: './excel-import.component.html',
  styleUrl: './excel-import.component.scss',
})
export class ExcelImportComponent implements OnInit, AfterViewInit {
  excelHeaders: string[] = [];
  excelRows: any[] = [];
  @ViewChild(MatSort) sort!: MatSort;

  banks: Bank[] = [];
  accounts: Account[] = [];
  filteredAccounts: Account[] = [];
  sources: Source[] = [];
  cards: Card[] = [];
  filteredCards: Card[] = [];
  selectedCard: Card | null = null;
  importOrigins: ImportOrigin[] = [];
  importProfiles: ImportProfile[] = [];
  filteredProfiles: ImportProfile[] = [];
  selectedOrigin: ImportOrigin | null = null;

  selectedBank: Bank | null = null;
  
  selectedAccount: Account | null = null;
  
  selectedProfile: ImportProfile | null = null;
  
  transactions: ImportTransaction[] = [];
  
  dataSource: MatTableDataSource<ImportTransaction> = new MatTableDataSource<ImportTransaction>([]);
  expenseCategories: ExpenseCategoryBase[] = [];
  incomeCategories: IncomeCategoryBase[] = [];
  isClassifying = false;
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
    'account'
  ];
  constructor(
    private bankService: BankService,
    private toastService: ToastService,
    private translateService: AppTranslateService,
    private incomeCategoyService: IncomeCategoryService,
    private expenseCategoryService: ExpenseCategoryService,
    private ruleCategorizerService: RuleCategorizerService,
    private utilsService: UtilsService,
    private transactionAiService: TransactionAiService,
    private transactionImportService: TransactionImportService,
    private accountService: AccountService,
    private sourceService: SourceService,
    private cardService: CardService,
    private importOriginsService: ImportOriginsService,
    private importProfilesService: ImportProfilesService,
  ) { }
  ngOnInit(): void {
    this.bankService.getBanks().subscribe({
      next: (res) => {
        this.banks = res.response;
      },
      error: (error) => {
        this.toastService.error(
          this.translateService.translateKey('ERROR_LOAD_BANKS'),
        );
      },
    });

    this.accountService.getAll().subscribe({
      next: (res) => {
        this.accounts = res.response;
      },
      error: (error) => {
        this.toastService.error(
          this.translateService.translateKey('ERROR_LOAD_ACCOUNTS'),
        );
      },
    });

    this.sourceService.getAll().subscribe({
      next: (res) => {
        this.sources = res.response;
      },
      error: (error) => {
        this.toastService.error(
          this.translateService.translateKey('ERROR_LOAD_SOURCES'),
        );
      },
    });

    this.incomeCategoyService.getAll().subscribe({
      next: (res) => {
        this.incomeCategories = res.response;
      },
      error: (error) => {
        this.toastService.error(
          this.translateService.translateKey('ERROR_LOAD_INCOMES_CATEGORIES'),
        );
      },
    });
    this.expenseCategoryService.getAll().subscribe({
      next: (res) => {
        this.expenseCategories = res.response;
      },
      error: (error) => {
        this.toastService.error(
          this.translateService.translateKey('ERROR_LOAD_EXPENSES_CATEGORIES'),
        );
      },
    });
    this.cardService.getAll().subscribe({
      next: (res) => {
        this.cards = res.response;
      },
      error: (error) => {
        this.toastService.error(
          this.translateService.translateKey('ERROR_LOAD_CARDS'),
        );
      },
    });
    this.importOriginsService.getOrigins().subscribe({
      next: (res) => {
        this.importOrigins = (res.response ?? []).filter((origin) => origin.active !== false);
      },
      error: () => {
        this.toastService.error('No se pudieron cargar los orígenes de importación');
      },
    });
    this.importProfilesService.getProfiles().subscribe({
      next: (res) => {
        this.importProfiles = (res.response ?? []).filter((profile) => profile.active !== false);
      },
      error: () => {
        this.toastService.error('No se pudieron cargar los perfiles de importación');
      },
    });
  }

  ngAfterViewInit() {
    this.dataSource.sort = this.sort;
  }

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
    this.selectedAccount = null;
    this.selectedCard = null;
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

  onAccountSelected(accountId: number) {
    const id = Number(accountId);
    const account = this.filteredAccounts.find((a) => a.id === id);
    if (!account) {
      console.warn('Account not found for selected bank');
      return;
    }
    this.selectedAccount = account;
    this.filterCardsByAccount(accountId);
    this.selectedCard = null;
    // Apply account to all selected transactions
    this.transactions.forEach((t) => {
      t.account_id = account.id;
      t.suggestedAccountId = account.id;
    });
    this.updateDataSource();
  }

  findColumnIndex(headers: string[], keywords: string[]): number {
    return headers.findIndex((h) => {
      if (!h) return false; //
      const header = this.utilsService.normalize(String(h));

      return keywords.some((k) => header.includes(k));
    });
  }

  private filterCardsByAccount(accountId: number) {
    this.filteredCards = this.cards.filter(c => c.account_id === accountId);
  }

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

      const headerRow = this.selectedProfile!.header_row_guess ?? 1;
      const headerIndex = headerRow - 1;

      this.excelHeaders = (rows[headerIndex] as any[]).map((h) =>
        h ? String(h).trim() : '',
      );
      this.excelRows = rows.slice(headerIndex + 1);

      const dateIndex = this.findColumnIndex(
        this.excelHeaders,
        this.selectedProfile!.columns['date'] ?? [],
      );
      const descriptionIndex = this.findColumnIndex(
        this.excelHeaders,
        this.selectedProfile!.columns['description'] ?? [],
      );

      const amountIndex = this.findColumnIndex(
        this.excelHeaders,
        this.selectedProfile!.columns['amount'] ?? [],
      );
      const balanceIndex = this.findColumnIndex(
        this.excelHeaders,
        this.selectedProfile!.columns['balance'] ?? [],
      );

      if (dateIndex === -1 || descriptionIndex === -1 || amountIndex === -1) {
        console.error('Column detection failed', this.excelHeaders);
        this.toastService.error('Excel format not recognized');
        return;
      }
      const validRows = this.excelRows.filter((row) => {
        const amount = this.utilsService.parseAmount(row[amountIndex]);
        // Drop rows without amount
        if (amount === null || amount === undefined || isNaN(amount) || amount === 0) {
          //console.log('Row without import:', row);
          return false;
        }
        return true;
      });
      console.log('Valid rows:', validRows);

      const tempTransactions: ImportTransaction[] = validRows.map((row) => ({
        date: row[dateIndex],
        description: row[descriptionIndex],
        amount: this.utilsService.parseAmount(row[amountIndex]),
        balance: this.utilsService.parseAmount(row[balanceIndex]),
        suggestedCategoryId: null,
        suggestedCategoryName: null,
        source_id: null,
        account_id: this.selectedAccount?.id ?? null,
        suggestedSourceId: null,
        suggestedAccountId: this.selectedAccount?.id ?? null,
        card_id: this.selectedCard?.id ?? null,
        ignore_in_analysis: !!this.selectedCard && this.utilsService.parseAmount(row[amountIndex]) < 0,
        selected: false,
      }));

      // Make sure rules are loaded/refreshed before local categorization.
      await this.ruleCategorizerService.refreshRules();

      const categorized = this.ruleCategorizerService.categorize(
        tempTransactions,
        this.incomeCategories,
        this.expenseCategories,
      );
      const uncategorized = categorized.filter(t => !t.suggestedCategoryId);
      categorized
        .filter(t => t.suggestedCategoryId)
        .forEach(t => this.suggestSourceForTransaction(t, t.suggestedCategoryId!));
      console.log('Uncategorized transactions:', uncategorized);

      this.transactions = categorized;
      this.updateDataSource();
      this.isClassifying = false;

//      const payload: ClassifyPayload = {
//        transactions: uncategorized.map((t, index) => ({
//          id: index,
//          type: t.amount < 0 ? 'expense' as const : 'income' as const,
//          description: (String(t.description)).trim(),
//          amount: Number(+t.amount),
//        })),
//        rules: [] // Rules are now managed on the backend
//      };
//      this.isClassifying = true; // activates spinner
//
//      this.transactionAiService.publicclassify(payload).subscribe({
//        next: res => {
//          const results = res?.response ?? [];
//          for (const classification of results) {
//            const tx = uncategorized[classification.id];
//            if (!tx) continue;
//            if (classification.category?.id) {
//              tx.suggestedCategoryId = classification.category.id;
//            } else if (classification.category?.suggested_new_category) {
//              tx.suggestedCategoryName = classification.category.suggested_new_category;
//            }
//          }
//          this.transactions = categorized; // table is rendered here
//          this.isClassifying = false;
//        },
//        error: err => {
//          console.error('Classification error:', err);
//          this.transactions = categorized; // still render data if AI fails
//          this.isClassifying = false;
//        }
//      });
    };

    reader.readAsBinaryString(file);
  }

  getCategories(t: ImportTransaction) {
    if (t.amount < 0) {
      return this.expenseCategories;
    }
    return this.incomeCategories;
  }

  onCategoryChange(transaction: ImportTransaction, categoryId: number) {
    transaction.suggestedCategoryId = categoryId;
    this.suggestSourceForTransaction(transaction, categoryId);
  }

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

    const transactionType: 'expense' | 'income' | 'investment' = transaction.amount < 0 ? 'expense' : 'income';

    this.sourceService.suggestSource(categoryId, transactionType).subscribe({
      next: (res) => {
        if (res && res.response && res.response.id) {
          transaction.suggestedSourceId = res.response.id;
          transaction.source_id = res.response.id;
          this.updateDataSource();
        } else {
          this.applySourceFallback(transaction);
        }
      },
      error: (err) => {
        console.warn('Source suggestion endpoint not available or failed, using fallback', err);
        this.applySourceFallback(transaction);
      }
    });
  }

  private findSourceByDescription(transaction: ImportTransaction): Source | null {
    const description = this.utilsService.normalize(String(transaction.description ?? ''));
    if (!description) return null;

    const expectedType = transaction.amount < 0 ? 'expense' : 'income';
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

  private applySourceFallback(transaction: ImportTransaction) {
    const expectedType = transaction.amount < 0 ? 'expense' : 'income';
    const sourceByType = this.sources.find((s) => s.type === expectedType);
    const fallbackSource = sourceByType ?? this.sources[0];

    transaction.suggestedSourceId = fallbackSource?.id ?? null;
    transaction.source_id = fallbackSource?.id ?? null;
    this.updateDataSource();
  }

  private filterAccountsByBank(bankId: number): void {
    this.filteredAccounts = this.accounts.filter((a) => a.bank_id === bankId);
  }

  updateDataSource(): void {
    this.dataSource.data = this.transactions;
    if (this.sort) {
      this.dataSource.sort = this.sort;
    }
  }

  toggleAll(checked: boolean) {
    this.transactions.forEach((t) => {
      t.selected = checked;
    });
  }
  isAllSelected(): boolean {
    return (
      this.transactions.length > 0 && this.transactions.every((t) => t.selected)
    );
  }
  isSomeSelected(): boolean {
    const selectedCount = this.transactions.filter((t) => t.selected).length;
    return selectedCount > 0 && selectedCount < this.transactions.length;
  }
  confirmImport() {
    const selected = this.transactions.filter((t) => t.selected);
    if (!selected.length) {
      this.toastService.error('Selecciona al menos una transacción');
      return;
    }

    const withoutCategory = selected.filter((t) => !t.suggestedCategoryId);
    if (withoutCategory.length > 0) {
      this.toastService.error('Hay transacciones sin categoría asignada');
      return;
    }

    const expenses = selected.filter((t) => t.amount < 0);
    const incomes = selected.filter((t) => t.amount >= 0);

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
    }));

  

    console.log('Expense bulk draft payload:', expensesDraftPayload);
    console.log('Income bulk draft payload:', incomesDraftPayload);

    const payload = {
      expenses: expensesDraftPayload,
      incomes: incomesDraftPayload
    };

    this.transactionImportService.importAtomic(payload).subscribe({
      next: (res) => {
        const inserted = res.response?.inserted ?? (res.response?.expenses_created ?? 0) + (res.response?.incomes_created ?? 0);
        const duplicates = res.response?.duplicates ?? 0;

        this.toastService.success(
          `¡Éxito! ${inserted} transacciones importadas. ${duplicates} duplicados ignorados.`
        );
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
