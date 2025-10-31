import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import * as ExcelJS from 'exceljs';
import { CurrencyEnum } from 'src/app/models/CurrencyBase';
import { ExpenseBase } from 'src/app/models/ExpenseBase';
import { IncomeBase } from 'src/app/models/IncomeBase';

@Component({
  selector: 'app-excel-import-component',
  imports: [CommonModule],
  templateUrl: './excel-import-component.html',
  styleUrl: './excel-import-component.scss',
})
export class ExcelImportComponent {
  incomes: IncomeBase[] = [];
  expenses: ExpenseBase[] = [];
  loading = false;
  fileName = '';

  keywordCategories = [
    { keyword: 'supermercado', category_id: 1 },
    { keyword: 'amazon', category_id: 2 },
    { keyword: 'nómina', category_id: 3 },
    { keyword: 'transferencia', category_id: 4 },
  ];

  keywordSources = [
    { keyword: 'empresa', source_id: 1 },
    { keyword: 'ingreso', source_id: 2 },
  ];

  async onFileSelected(event: any) {
    const file = event.target.files[0];
    if (!file) return;

    this.fileName = file.name;
    this.loading = true;

    const buffer = await file.arrayBuffer();
    const workbook = new ExcelJS.Workbook();
    await workbook.xlsx.load(buffer);
    const sheet = workbook.worksheets[0];

    this.incomes = [];
    this.expenses = [];

    sheet.eachRow((row, index) => {
      if (index === 1) return; // saltar encabezado

      const [
        ,
        date,
        category,
        subcategory,
        description,
        comment,
        ,
        amount
      ] = row.values as any[];

      const amountNum = parseFloat(String(amount).replace(',', '.'));
      if (isNaN(amountNum)) return;

      const isIncome = amountNum > 0;

      const foundCat = this.keywordCategories.find(k =>
        (description || '').toLowerCase().includes(k.keyword)
      );

      const foundSource = this.keywordSources.find(k =>
        (description || '').toLowerCase().includes(k.keyword)
      );

      if (isIncome) {
        this.incomes.push({
          id: Date.now() + index,
          name: description || 'Ingreso',
          description: comment || description,
          amount: amountNum,
          date: date,
          currency: CurrencyEnum.Euro,
          user_id: 1,
          source_id: foundSource?.source_id || 0,
          category_id: foundCat?.category_id || 0,
          account_id: 1,
        });
      } else {
        this.expenses.push({
          id: Date.now() + index,
          name: description || 'Gasto',
          description: comment || description,
          amount: Math.abs(amountNum),
          date: date,
          currency: CurrencyEnum.Euro,
          category_id: foundCat?.category_id || 0,
          place_id: 1,
          user_id: 1,
          account_id: 1,
        });
      }
    });

    this.loading = false;
  }

  saveToDatabase() {
    // Aquí puedes llamar a tu servicio API para guardar los ingresos/gastos
    console.log('💾 Guardando ingresos:', this.incomes);
    console.log('💾 Guardando gastos:', this.expenses);
    alert('Transacciones procesadas y listas para guardar.');
  }
}
