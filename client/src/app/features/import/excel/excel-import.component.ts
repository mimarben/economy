import { Component, OnInit } from '@angular/core';
import * as XLSX from 'xlsx';

import { ExpenseCategoryBase } from '@expenses_models/ExpenseCategoryBase';
import { ExpenseCategoryService } from '@app/services/expenses/expense-category.service';
import { IncomeCategoryBase } from '@incomes_models/IncomeCategoryBase';
import { IncomeCategoryService } from '@incomes_services/income-category.service';

import { RuleCategorizerService } from '@import_services/rule-categorizer.service';
import { BankProfile } from "@import_models/BankProfile";
import { BANK_PROFILES } from "@app/core/import/bank-profiles.const";
import { BankService } from '@finance_services/bank.service';
import { BankBase as Bank } from '@finance_models/BankBase';
import { ImportTransaction } from '@import_models/import-transaction.model';
import { ToastService } from '@core_services/toast.service';

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
  displayedColumns = [
    "select",
    "date",
    "description",
    "amount",
    "balance",
    "category"
  ];
  constructor(private bankService: BankService,
    private toastService: ToastService,
    private translateService: AppTranslateService,
    private incomeCategoyService: IncomeCategoryService,
    private expenseCategoryService: ExpenseCategoryService,
    private ruleCategorizerService: RuleCategorizerService
  ) {

  }
  ngOnInit(): void {

    this.bankService.getBanks().subscribe({
      next: (res) => {
        this.banks = res.response
      },
      error: (error) => {
        this.toastService.error(this.translateService.translateKey("ERROR_LOAD_BANKS"))
      }
    });
    this.incomeCategoyService.getAll().subscribe({
      next: (res) => {
        this.incomeCategories = res.response
      },
      error: (error) => {
        this.toastService.error(this.translateService.translateKey("ERROR_LOAD_INCOMES_CATEGORIES"))
      }
    });
    this.expenseCategoryService.getAll().subscribe({
      next: (res) => {
        this.expenseCategories = res.response
      },
      error: (error) => {
        this.toastService.error(this.translateService.translateKey("ERROR_LOAD_EXPENSES_CATEGORIES"))
      }
    })

  }

  onBankSelected(bankId: number) {
    const id = Number(bankId);
    const bank = this.banks.find(b => b.id === id);
    if (!bank) {
      console.warn("Bank not found");
      this.toastService.success(this.translateService.translateKey('BANK.NOT_FOUND'));
      return;
    }
    this.selectedBank = bank;
    console.log("Selected bank:", bank);
    // buscar profile
    const profile = BANK_PROFILES.find(
      p => p.name.toLowerCase() === bank.name.toLowerCase()
    );
    if (!profile) {
      console.warn("Import profile not found for bank", bank.name);
      this.toastService.error(this.translateService.translateKey("BANK.PROFILE_NOT_FOUND"));
      return;
    }
    this.selectedProfile = profile;
    console.log("Selected profile:", profile);
  }

  findColumnIndex(headers: string[], keywords: string[]): number {

    return headers.findIndex(h => {

      const header = h.toLowerCase();

      return keywords.some(k => header.includes(k));

    });

  }

  private parseAmount(value: any): number {
    if (value == null) return 0;
    if (typeof value === 'number') return value;

    let str = String(value)
      .trim()
      .replace(/[€\s]/g, '')
      .replace('−', '-');

    const lastDot = str.lastIndexOf('.');
    const lastComma = str.lastIndexOf(',');

    if (lastComma > lastDot) {
      // formato europeo 1.501,70
      str = str.replace(/\./g, '').replace(',', '.');
    } else if (lastDot > lastComma) {
      // formato inglés 1,501.70
      str = str.replace(/,/g, '');
    }

    const num = Number(str);

    console.log("Valor raw:", value, "parsed:", num);

    return Number.isNaN(num) ? 0 : num;
  }

  onFileChange(event: Event) {

    if (!this.selectedProfile) {
      console.warn("Import profile not found for bank", this.selectedBank?.name);
      this.toastService.error(
        this.translateService.translateKey("BANK.PROFILE_NOT_FOUND")
      );
      return;
    }

    const input = event.target as HTMLInputElement;

    if (!input.files?.length) return;

    const file = input.files[0];

    const reader = new FileReader();

    reader.onload = (e: any) => {

      const workbook = XLSX.read(e.target.result, {
        type: 'binary'
      });

      const sheetName = workbook.SheetNames[0];
      const sheet = workbook.Sheets[sheetName];

      const rows: any[][] = XLSX.utils.sheet_to_json(sheet, {
        header: 1,
        raw: false
      });

      const headerRow = this.selectedProfile!.headerRowGuess ?? 1;
      const headerIndex = headerRow - 1;

      this.excelHeaders = rows[headerIndex] as string[];
      this.excelRows = rows.slice(headerIndex + 1);

      const dateIndex = this.findColumnIndex(
        this.excelHeaders,
        this.selectedProfile!.columns.date
      );

      const descriptionIndex = this.findColumnIndex(
        this.excelHeaders,
        this.selectedProfile!.columns.description
      );

      const amountIndex = this.findColumnIndex(
        this.excelHeaders,
        this.selectedProfile!.columns.amount
      );
      const balanceIndex = this.findColumnIndex(
        this.excelHeaders,
        this.selectedProfile!.columns.balance
      );

      this.transactions = this.excelRows.map(row => ({
        date: row[dateIndex],
        description: row[descriptionIndex],
        amount: this.parseAmount(row[amountIndex]),
        balance: this.parseAmount(row[balanceIndex]),
        suggestedCategoryId: 0,
        selected: false
      }));

      console.log("Transactions:", this.transactions);
      this.transactions = this.ruleCategorizerService.categorize(
        this.transactions,
        this.incomeCategories,
        this.expenseCategories
      );
      console.log("Transactions:", this.transactions);
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

  this.transactions.forEach(t => {
    t.selected = checked;
  });

}
isAllSelected(): boolean {

  return this.transactions.length > 0 &&
         this.transactions.every(t => t.selected);

}
isSomeSelected(): boolean {

  const selectedCount = this.transactions.filter(t => t.selected).length;

  return selectedCount > 0 && selectedCount < this.transactions.length;

}
  confirmImport() {

    const selected = this.transactions.filter(t => t.selected);

    console.log("Transactions to import:", selected);

  }
}
