import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import * as ExcelJS from 'exceljs';
import { CurrencyEnum } from 'src/app/models/CurrencyBase';
import { ExpenseBase } from 'src/app/models/ExpenseBase';
import { IncomeBase } from 'src/app/models/IncomeBase';

@Component({
  selector: 'app-excel-import',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './excel-import-component.html',
  styleUrls: ['./excel-import-component.scss'],
})
export class ExcelImportComponent {
  incomes: IncomeBase[] = [];
  expenses: ExpenseBase[] = [];
  loading = false;
  fileName = '';

  private readonly keywordCategories = [
    { keyword: 'supermercado', category_id: 1 },
    { keyword: 'amazon', category_id: 2 },
    { keyword: 'nómina', category_id: 3 },
    { keyword: 'transferencia', category_id: 4 },
  ];

  private readonly keywordSources = [
    { keyword: 'empresa', source_id: 1 },
    { keyword: 'ingreso', source_id: 2 },
  ];

  /** Evento al seleccionar un archivo Excel */
  async onFileSelected(event: Event): Promise<void> {
    const input = event.target as HTMLInputElement;
    const file = input?.files?.[0];
    if (!file) return;

    this.fileName = file.name;
    this.loading = true;

    try {
      const workbook = await this.loadWorkbook(file);
      const sheet = workbook.worksheets[0];
      this.parseSheet(sheet);
      alert(`✅ Archivo procesado: ${this.incomes.length} ingresos y ${this.expenses.length} gastos detectados.`);
    } catch (err) {
      console.error('❌ Error procesando el archivo:', err);
      alert('Error al procesar el archivo Excel.');
    } finally {
      this.loading = false;
    }
  }

  /** Carga el archivo Excel en memoria */
  private async loadWorkbook(file: File): Promise<ExcelJS.Workbook> {
    const buffer = await file.arrayBuffer();
    const workbook = new ExcelJS.Workbook();
    await workbook.xlsx.load(buffer);
    return workbook;
  }

  /** Parsea las filas de la hoja Excel */
  private parseSheet(sheet: ExcelJS.Worksheet): void {
    this.incomes = [];
    this.expenses = [];

    sheet.eachRow((row, index) => {
      if (index === 1) return; // Saltar encabezado

      const [, date, , , description, comment, , amount] = row.values as any[];
      const amountNum = this.toNumber(amount);
      if (amountNum === null) return;

      const recordData = {
        id: Date.now() + index,
        name: description || (amountNum > 0 ? 'Ingreso' : 'Gasto'),
        description: comment || description || '',
        amount: Math.abs(amountNum),
        date,
        currency: CurrencyEnum.Euro,
        user_id: 1,
        account_id: 1,
      };

      const category_id = this.findCategory(description);
      const source_id = this.findSource(description);

      if (amountNum > 0) {
        this.incomes.push({ ...recordData, category_id, source_id });
      } else {
        this.expenses.push({
          ...recordData,
          category_id,
          place_id: 1,
        });
      }
    });
  }

  /** Convierte texto o número en float seguro */
  private toNumber(value: any): number | null {
    const num = parseFloat(String(value).replace(',', '.'));
    return isNaN(num) ? null : num;
  }

  /** Busca categoría por palabra clave */
  private findCategory(description: string): number {
    const found = this.keywordCategories.find(k =>
      (description || '').toLowerCase().includes(k.keyword)
    );
    return found?.category_id ?? 0;
  }

  /** Busca fuente por palabra clave */
  private findSource(description: string): number {
    const found = this.keywordSources.find(k =>
      (description || '').toLowerCase().includes(k.keyword)
    );
    return found?.source_id ?? 0;
  }

  /** Simula guardado en base de datos */
  saveToDatabase(): void {
    console.log('💾 Guardando ingresos:', this.incomes);
    console.log('💾 Guardando gastos:', this.expenses);
    alert(`Guardadas ${this.incomes.length + this.expenses.length} transacciones.`);
  }
}
