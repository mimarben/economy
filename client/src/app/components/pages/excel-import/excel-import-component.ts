import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import * as ExcelJS from 'exceljs';
import { Worksheet, Row } from 'exceljs';
import { CurrencyEnum } from 'src/app/models/CurrencyBase';
import { ExpenseBase } from 'src/app/models/ExpenseBase';
import { IncomeBase } from 'src/app/models/IncomeBase';
import { UtilsService } from '@utils/utils.service';

interface ColumnMap {
  [key: string]: number;
}

interface FormatDetection {
  format: keyof typeof COLUMN_MAPS | null;
  headerIndices: ColumnMap | null;
  headerRowNumber: number;
}

const COLUMN_MAPS = {
  ing: {
    requiredHeaders: ['F. VALOR', 'DESCRIPCIÓN', 'IMPORTE (€)', 'SALDO (€)'],
    map: {
      date: 'F. VALOR',
      category: 'CATEGORÍA',
      subcategory: 'SUBCATEGORÍA',
      description: 'DESCRIPCIÓN',
      comment: 'COMENTARIO',
      image: 'IMAGEN',
      amount: 'IMPORTE (€)',
      balance: 'SALDO (€)',
    }
  },
  carrefour_pass: {
    requiredHeaders: ['FECHA', 'CONCEPTO', 'CARGO/ABONO'],
    map: {
      date: 'FECHA',
      description: 'CONCEPTO',
      mode: 'MODO DE PAGO',
      amount: 'CARGO/ABONO',
      deferrable: 'APLAZABLE'
    }
  },
};

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

  private currentFormat: keyof typeof COLUMN_MAPS | null = null;

  private readonly keywordCategories = [
    { keyword: 'mercadona', category_id: 1 },
    { keyword: 'carrefour', category_id: 1 },
    { keyword: 'supermercado', category_id: 1 },
    { keyword: 'gadis', category_id: 1 },
    { keyword: 'amazon', category_id: 2 },
    { keyword: 'nómina', category_id: 3 },
    { keyword: 'nomina', category_id: 3 },
    { keyword: 'transferencia', category_id: 4 },
    { keyword: 'fruta', category_id: 1 },
    { keyword: 'salon', category_id: 5 },
    { keyword: 'belleza', category_id: 5 },
  ];

  private readonly keywordPlaces = [
    { keyword: 'mercadona', place_id: 2 },
    { keyword: 'carrefour', place_id: 1 },
    { keyword: 'gadis', place_id: 6 },
    { keyword: 'arte de la fruta', place_id: 5 },
    { keyword: 'el arte', place_id: 5 },
    { keyword: 'amazon', place_id: 3 },
    { keyword: 'salon', place_id: 7 },
  ];

  private readonly keywordSources = [
    { keyword: 'empresa', source_id: 1 },
    { keyword: 'ingreso', source_id: 2 },
    { keyword: 'nómina', source_id: 1 },
    { keyword: 'salario', source_id: 1 },
  ];

  constructor(private utils: UtilsService) {}

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

      const detection = this.identifyFormat(sheet);

      if (!detection.format || !detection.headerIndices) {
        alert('❌ ERROR: Formato de archivo Excel no reconocido.');
        return;
      }

      this.currentFormat = detection.format;
      this.parseSheet(sheet, detection.headerIndices, detection.headerRowNumber);

      alert(
        `✅ Archivo (${detection.format}) procesado:\n${this.incomes.length} ingresos y ${this.expenses.length} gastos detectados.`
      );
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

  /** Normaliza texto eliminando espacios extras y caracteres especiales */
  private normalize(val: any): string {
    return String(val ?? '')
      .replace(/[\uFEFF\u00A0\u2000-\u200F\u2028\u2029\u200B-\u200D]/g, '')
      .replace(/[\x00-\x1F\x7F]/g, '')
      .replace(/\s+/g, ' ')
      .trim()
      .toUpperCase();
  }

  /** Identifica el formato del archivo y devuelve los índices de las columnas clave */
  private identifyFormat(sheet: ExcelJS.Worksheet): FormatDetection {
    let headerRow: ExcelJS.Row | null = null;
    let headers: string[] = [];
    let headerRowNumber = 0;
    const maxRowsToCheck = 50;

    // Buscar la fila de cabeceras
    for (let rowIndex = 1; rowIndex <= maxRowsToCheck; rowIndex++) {
      const row = sheet.getRow(rowIndex);
      const values = row.values as any[];

      if (!values || values.length === 0) continue;

      // row.values es [undefined, col1, col2, col3...] en ExcelJS
      // Normalizar valores empezando desde índice 1
      const normalized: string[] = [];
      for (let i = 1; i < values.length; i++) {
        const v = values[i];
        if (v != null && v !== '') {
          normalized.push(this.normalize(v));
        } else {
          normalized.push(''); // Mantener posición para columnas vacías
        }
      }

      if (normalized.filter(n => n !== '').length === 0) continue;

      console.log(`Fila ${rowIndex} valores raw:`, values);
      console.log(`Fila ${rowIndex} normalizada:`, normalized);

      // Comprobar cada formato
      for (const formatName in COLUMN_MAPS) {
        const format = COLUMN_MAPS[formatName as keyof typeof COLUMN_MAPS];
        const required = format.requiredHeaders.map(h => this.normalize(h));

        // Verificar si todos los headers requeridos están presentes
        const isMatch = required.every(req =>
          normalized.some(norm => norm !== '' && (norm.includes(req) || req.includes(norm)))
        );

        if (isMatch) {
          headerRow = row;
          headers = normalized;
          headerRowNumber = rowIndex;
          console.log(`✅ Cabeceras detectadas fila ${rowIndex}: formato ${formatName}`);
          console.log('Headers encontrados:', headers);
          break;
        }
      }
      if (headerRow) break;
    }

    if (!headerRow) {
      console.error('❌ No se encontraron cabeceras válidas');
      return { format: null, headerIndices: null, headerRowNumber: 0 };
    }

    // Mapear columnas según el formato detectado
    for (const formatName in COLUMN_MAPS) {
      const format = COLUMN_MAPS[formatName as keyof typeof COLUMN_MAPS];
      const required = format.requiredHeaders.map(h => this.normalize(h));

      const hasAllRequired = required.every(req =>
        headers.some(h => h !== '' && (h.includes(req) || req.includes(h)))
      );

      if (hasAllRequired) {
        const headerIndices: ColumnMap = {};

        // Mapear cada columna
        for (const [key, headerName] of Object.entries(format.map)) {
          if (!headerName) continue;

          const normalizedHeaderName = this.normalize(headerName);

          // Buscar en el array normalizado (que empieza en índice 0)
          const arrayIndex = headers.findIndex(h =>
            h !== '' && (h.includes(normalizedHeaderName) || normalizedHeaderName.includes(h))
          );

          if (arrayIndex > -1) {
            // Convertir índice de array a índice de columna ExcelJS (1-based)
            headerIndices[key] = arrayIndex + 1;
            console.log(`Columna "${key}" (${headerName}) → array index ${arrayIndex} → excel col ${arrayIndex + 1}`);
          }
        }

        console.log('Índices de columnas finales:', headerIndices);
        return {
          format: formatName as keyof typeof COLUMN_MAPS,
          headerIndices,
          headerRowNumber
        };
      }
    }

    return { format: null, headerIndices: null, headerRowNumber: 0 };
  }

  /** Parsea las filas de la hoja Excel */
  private parseSheet(
    sheet: ExcelJS.Worksheet,
    headerIndices: ColumnMap,
    headerRowNumber: number
  ): void {
    this.incomes = [];
    this.expenses = [];

    let processedRows = 0;
    let skippedRows = 0;

    sheet.eachRow((row: Row, rowIndex: number) => {
      // Saltar filas hasta después de la cabecera
      if (rowIndex <= headerRowNumber) return;

      // LOG: Ver toda la fila para debug
      if (rowIndex <= headerRowNumber + 3) {
        console.log(`\n=== FILA ${rowIndex} ===`);
        console.log('Valores de la fila:', row.values);
        console.log('Header indices:', headerIndices);
      }

      // --- Extraer fecha ---
      const dateCell = row.getCell(headerIndices['date']);
      let rawDate = dateCell?.value;

      console.log(`Fila ${rowIndex} - Celda fecha (col ${headerIndices['date']}):`, rawDate, typeof rawDate);

      // Manejar fórmulas
      if (rawDate && typeof rawDate === 'object' && 'result' in rawDate) {
        rawDate = rawDate.result;
      }

      let rawDateValue: string | number | Date | null = null;

      if (rawDate instanceof Date) {
        rawDateValue = rawDate;
      } else if (typeof rawDate === 'string' || typeof rawDate === 'number') {
        rawDateValue = rawDate;
      } else {
        rawDateValue = null;
      }

      console.log(`Fila ${rowIndex} - Raw Date Value:`, rawDateValue);

      const dateValue = this.utils.parseToSafeDate(rawDateValue);

      console.log(`Fila ${rowIndex} - Parsed Date:`, dateValue);

      // --- Extraer monto ---
      const amountCell = row.getCell(headerIndices['amount']);
      let rawAmount = amountCell?.value;

      console.log(`Fila ${rowIndex} - Celda amount (col ${headerIndices['amount']}):`, rawAmount, typeof rawAmount);

      // Manejar fórmulas
      if (rawAmount && typeof rawAmount === 'object' && 'result' in rawAmount) {
        rawAmount = rawAmount.result;
      }

      const amountNum = this.toNumber(rawAmount);

      if (amountNum === null) {
        console.warn(`Fila ${rowIndex}: Monto inválido, saltando`);
        skippedRows++;
        return;
      }

      // --- Descripción ---
      const descriptionCell = row.getCell(headerIndices['description']);
      let description = descriptionCell?.value;

      if (description && typeof description === 'object' && 'result' in description) {
        description = description.result;
      }

      description = String(description || '').trim();

      // --- Comentario (opcional) ---
      let comment = '';
      if (headerIndices['comment']) {
        const commentCell = row.getCell(headerIndices['comment']);
        let commentValue = commentCell?.value;
        if (commentValue && typeof commentValue === 'object' && 'result' in commentValue) {
          commentValue = commentValue.result;
        }
        comment = String(commentValue || '').trim();
      }

      // --- Construir registro base ---
      const recordData = {
        id: Date.now() + rowIndex,
        name: description || (amountNum > 0 ? 'Ingreso' : 'Gasto'),
        description,
        comment,
        amount: Math.abs(amountNum),
        date: dateValue ? dateValue.toISOString() : new Date().toISOString(),
        currency: CurrencyEnum.Euro,
        user_id: 1,
        account_id: 1,
      };

      // --- Categoría, fuente y lugar ---
      const category_id = this.findCategory(description);
      const source_id = this.findSource(description);
      const place_id = this.findPlace(description);

      // --- Separar ingresos y gastos ---
      if (amountNum > 0) {
        this.incomes.push({ ...recordData, category_id, source_id });
      } else {
        this.expenses.push({ ...recordData, category_id, place_id: place_id || 1 });
      }

      processedRows++;
    });

    console.log(`✅ Procesadas ${processedRows} filas, saltadas ${skippedRows}`);
  }

  /** Conversión segura de número */
  private toNumber(value: any): number | null {
    if (value === null || value === undefined || value === '') return null;

    // Si es string, limpiar y convertir
    if (typeof value === 'string') {
      // Ignorar si es texto no numérico
      if (value.toLowerCase() === 'contado' ||
          value.toLowerCase() === 'aplazable' ||
          isNaN(parseFloat(value.replace(',', '.')))) {
        return null;
      }
      const cleaned = value.replace(/[^\d,.-]/g, '').replace(',', '.');
      const num = parseFloat(cleaned);
      return isNaN(num) ? null : num;
    }

    // Si es número, devolver directamente
    if (typeof value === 'number') {
      return isNaN(value) ? null : value;
    }

    return null;
  }

  /** Buscar categoría por palabra clave */
  private findCategory(description: string): number {
    const lowerDesc = (description || '').toLowerCase();
    const found = this.keywordCategories.find(k =>
      lowerDesc.includes(k.keyword.toLowerCase())
    );
    return found?.category_id ?? 0;
  }

  /** Buscar lugar por palabra clave */
  private findPlace(description: string): number | null {
    const lowerDesc = (description || '').toLowerCase();
    const found = this.keywordPlaces.find(k =>
      lowerDesc.includes(k.keyword.toLowerCase())
    );
    return found?.place_id ?? null;
  }

  /** Buscar fuente por palabra clave */
  private findSource(description: string): number {
    const lowerDesc = (description || '').toLowerCase();
    const found = this.keywordSources.find(k =>
      lowerDesc.includes(k.keyword.toLowerCase())
    );
    return found?.source_id ?? 0;
  }

  /** Simula guardado en base de datos */
  saveToDatabase(): void {
    console.log(`💾 Guardando ingresos (${this.incomes.length}) y gastos (${this.expenses.length})`);
    console.log('Ingresos:', this.incomes);
    console.log('Gastos:', this.expenses);
    alert(`Guardadas ${this.incomes.length + this.expenses.length} transacciones.`);
  }
}
