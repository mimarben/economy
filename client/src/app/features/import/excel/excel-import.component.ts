import { Component, OnInit } from '@angular/core';
import * as XLSX from 'xlsx';

import { ExpenseCategoryBase } from '@expenses_models/ExpenseCategoryBase';
import { ExpenseCategoryService } from '@app/services/expenses/expense-category.service';
import { IncomeCategoryBase } from '@incomes_models/IncomeCategoryBase';
import { IncomeCategoryService } from '@incomes_services/income-category.service';
import { UtilsService } from '@utils/utils.service';
import { TransactionAiService } from '@services/ai/transaction-ai.service';
import { RuleCategorizerService } from '@import_services/rule-categorizer.service';
import { ToastService } from '@core_services/toast.service';
import { TransactionImportService } from '@app/services/import/transaction-import.service';

import { BankProfile } from '@import_models/BankProfile';
import { BANK_PROFILES } from '@app/core/import/bank-profiles.const';
import { BankService } from '@finance_services/bank.service';
import { BankBase as Bank } from '@finance_models/BankBase';
import { ImportTransaction } from '@import_models/import-transaction.model';
import { ClassifyRequest, ClassifyResult, ClassifyPayload } from '@import_models/classify-request-ai';

import { AppTranslateService } from '@utils/app-translate.service';
import { TranslateModule } from '@ngx-translate/core';
import { MaterialModule } from '@utils/material.module';
import { FormsModule } from '@angular/forms';
@Component({
  selector: 'app-excel-import',
  imports: [TranslateModule, MaterialModule, FormsModule],
  templateUrl: './excel-import.component.html',
  styleUrl: './excel-import.component.scss',
})
export class ExcelImportComponent implements OnInit {
  excelHeaders: string[] = [];
  excelRows: any[] = [];
  banks: Bank[] = [];
  selectedBank: Bank | null = null;
  selectedProfile: BankProfile | null = null;
  transactions: ImportTransaction[] = [];
  expenseCategories: ExpenseCategoryBase[] = [];
  incomeCategories: IncomeCategoryBase[] = [];
  isClassifying = false;
  displayedColumns = [
    'select',
    'date',
    'description',
    'amount',
    'balance',
    'category',
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
    private transactionImportService: TransactionImportService
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
    console.log('Selected bank:', bank);
    // buscar profile
    const profile = BANK_PROFILES.find(
      (p) => p.name.toLowerCase() === bank.name.toLowerCase(),
    );
    if (!profile) {
      console.warn('Import profile not found for bank', bank.name);
      this.toastService.error(
        this.translateService.translateKey('BANK.PROFILE_NOT_FOUND'),
      );
      return;
    }
    this.selectedProfile = profile;
    console.log('Selected profile:', profile);
  }

  findColumnIndex(headers: string[], keywords: string[]): number {
    return headers.findIndex((h) => {
      if (!h) return false; //
      const header = this.utilsService.normalize(String(h));

      return keywords.some((k) => header.includes(k));
    });
  }

  onFileChange(event: Event) {
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

    reader.onload = (e: any) => {
      const workbook = XLSX.read(e.target.result, {
        type: 'binary',
      });

      const sheetName = workbook.SheetNames[0];
      const sheet = workbook.Sheets[sheetName];

      const rows: any[][] = XLSX.utils.sheet_to_json(sheet, {
        header: 1,
        raw: false,
      });

      const headerRow = this.selectedProfile!.headerRowGuess ?? 1;
      const headerIndex = headerRow - 1;

      this.excelHeaders = (rows[headerIndex] as any[]).map((h) =>
        h ? String(h).trim() : '',
      );
      this.excelRows = rows.slice(headerIndex + 1);

      const dateIndex = this.findColumnIndex(
        this.excelHeaders,
        this.selectedProfile!.columns.date,
      );
      const descriptionIndex = this.findColumnIndex(
        this.excelHeaders,
        this.selectedProfile!.columns.description,
      );

      const amountIndex = this.findColumnIndex(
        this.excelHeaders,
        this.selectedProfile!.columns.amount,
      );
      const balanceIndex = this.findColumnIndex(
        this.excelHeaders,
        this.selectedProfile!.columns.balance,
      );

      if (dateIndex === -1 || descriptionIndex === -1 || amountIndex === -1) {
        console.error('Column detection failed', this.excelHeaders);
        this.toastService.error('Excel format not recognized');
        return;
      }
      const validRows = this.excelRows.filter((row) => {
        const amount = this.utilsService.parseAmount(row[amountIndex]);
        // eliminar filas sin importe
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
        selected: false,
      }));

      const categorized = this.ruleCategorizerService.categorize(
        tempTransactions,
        this.incomeCategories,
        this.expenseCategories,
      );
      const uncategorized = categorized.filter(t => !t.suggestedCategoryId);

      console.log('Uncategorized transactions:', uncategorized);

      const payload: ClassifyPayload = {
        transactions: uncategorized.map((t, index) => ({
          id: index,
          type: t.amount < 0 ? 'expense' as const : 'income' as const,
          description: (String(t.description)).trim(),
          amount: Number(+t.amount),
        })),
        rules: [] // Rules are now managed on the backend
      };
      console.log('Payload:', JSON.stringify(payload), payload);

      this.isClassifying = true; // ← activa spinner

      this.transactionAiService.publicclassify(payload).subscribe({
        next: res => {
          const results = res?.response ?? [];
          for (const classification of results) {
            const tx = uncategorized[classification.id];
            if (!tx) continue;
            if (classification.category?.id) {
              tx.suggestedCategoryId = classification.category.id;
            } else if (classification.category?.suggested_new_category) {
              tx.suggestedCategoryName = classification.category.suggested_new_category;
            }
          }
          this.transactions = categorized; // ← tabla aparece aquí
          this.isClassifying = false;
        },
        error: err => {
          console.error('Error en classify:', err);
          this.transactions = categorized; // ← muestra igualmente si falla la IA
          this.isClassifying = false;
        }
      });
    };

    reader.readAsBinaryString(file);
  }

  getCategories(t: ImportTransaction) {
    if (t.amount < 0) {
      return this.expenseCategories;
    }
    return this.incomeCategories;
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
    }));

    const incomesDraftPayload = incomes.map((t) => ({
      name: String(t.description).trim().slice(0, 255),
      description: String(t.description).trim(),
      amount: Number(t.amount),
      date: t.date,
      category_id: t.suggestedCategoryId,
    }));

    // IMPORTANTE:
    // Hacer 2 llamadas separadas (/expenses/bulk y /incomes/bulk) NO garantiza atomicidad global.
    // Para "todo o nada" real entre gastos+ingresos hace falta 1 endpoint backend único
    // que envuelva ambas inserciones en la misma transacción.
    // -> IMPLEMENTADO: Se llama al nuevo endpoint único y atómico.

    console.log('Expense bulk draft payload:', expensesDraftPayload);
    console.log('Income bulk draft payload:', incomesDraftPayload);

    const payload = {
      expenses: expensesDraftPayload,
      incomes: incomesDraftPayload
    };

    this.transactionImportService.importAtomic(payload).subscribe({
      next: (res) => {
        this.toastService.success(
          `¡Éxito! Importados ${res.response?.expenses_created || 0} gastos y ${res.response?.incomes_created || 0} ingresos en una transacción.`
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
