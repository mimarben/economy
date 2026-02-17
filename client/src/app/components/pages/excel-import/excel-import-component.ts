import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import * as ExcelJS from 'exceljs';
import { Worksheet, Row } from 'exceljs';
import { CurrencyEnum } from '@core_models/CurrencyBase';
import { ExpenseBase } from '@expenses_models/ExpenseBase';
import { IncomeBase } from '@incomes_models/IncomeBase';
import { UtilsService } from '@utils/utils.service';
import { ExpenseCategoryService } from '@expenses_services/expense-category.service';
import { IncomeCategoryService } from '@incomes_services/income-category.service';
import { ExpenseService } from '@expenses_services/expense.service';
import { IncomeService } from '@incomes_services/income.service';
import { ExpenseCategoryBase } from '@expenses_models/ExpenseCategoryBase';
import { IncomeCategoryBase } from '@incomes_models/IncomeCategoryBase';

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
  imports: [CommonModule, FormsModule],
  templateUrl: './excel-import-component.html',
  styleUrls: ['./excel-import-component.css'],
})
export class ExcelImportComponent {
  incomes: IncomeBase[] = [];
  expenses: ExpenseBase[] = [];

  // Listas de referencia cargadas de BD
  expenseCategories: ExpenseCategoryBase[] = [];
  incomeCategories: IncomeCategoryBase[] = [];

  // Transacciones pendientes de revisión
  pendingTransactions: any[] = [];

  loading = false;
  fileName = '';

  private currentFormat: keyof typeof COLUMN_MAPS | null = null;

  // Mantenemos las keywords para la pre-clasificación
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

  constructor(
    private utils: UtilsService,
    private expenseCategoryService: ExpenseCategoryService,
    private incomeCategoryService: IncomeCategoryService,
    private expenseService: ExpenseService,
    private incomeService: IncomeService
  ) {}

  ngOnInit() {
    this.loadCategories();
  }

  loadCategories() {
    this.expenseCategoryService.getAll().subscribe(res => {
      if (res.response) this.expenseCategories = res.response;
    });
    this.incomeCategoryService.getAll().subscribe(res => {
      if (res.response) this.incomeCategories = res.response;
    });
  }

  /** Evento al seleccionar un archivo Excel */
  async onFileSelected(event: Event): Promise<void> {
    const input = event.target as HTMLInputElement;
    const file = input?.files?.[0];
    if (!file) return;

    this.fileName = file.name;
    this.loading = true;
    this.pendingTransactions = []; // Reset

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
          break;
        }
      }
      if (headerRow) break;
    }

    if (!headerRow) {
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
          }
        }

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
    this.pendingTransactions = [];

    sheet.eachRow((row: Row, rowIndex: number) => {
      // Saltar filas hasta después de la cabecera
      if (rowIndex <= headerRowNumber) return;

      // --- Extraer fecha ---
      const dateCell = row.getCell(headerIndices['date']);
      let rawDate = dateCell?.value;

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

      const dateValue = this.utils.parseToSafeDate(rawDateValue);

      // --- Extraer monto ---
      const amountCell = row.getCell(headerIndices['amount']);
      let rawAmount = amountCell?.value;

      // Manejar fórmulas
      if (rawAmount && typeof rawAmount === 'object' && 'result' in rawAmount) {
        rawAmount = rawAmount.result;
      }

      const amountNum = this.toNumber(rawAmount);

      if (amountNum === null) {
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

      // --- Pre-categorización ---
      const type = amountNum > 0 ? 'income' : 'expense';
      const category_id = this.findCategory(description);
      const source_id = this.findSource(description);
      const place_id = this.findPlace(description);

      // --- Construir objeto pendiente ---
      this.pendingTransactions.push({
        id: Date.now() + rowIndex, // ID temporal
        date: dateValue ? dateValue.toISOString() : new Date().toISOString(),
        description,
        comment,
        amount: amountNum,
        type,
        category_id, // Pre-filled or 0
        source_id: source_id || 1, // Default source
        place_id: place_id || 1, // Default place
        selected: true // Checkbox para importar
      });
    });
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

  // --- Métodos de UI ---

  getCategoryName(id: number, type: 'income' | 'expense'): string {
    const list = type === 'income' ? this.incomeCategories : this.expenseCategories;
    return list.find(c => c.id === id)?.name || 'Sin Categoría';
  }

  onCategoryChange(transaction: any, event: any) {
    const value = event.target.value;
    if (value === 'NEW') {
      this.openCreateCategoryModal(transaction);
      // Reset select to previous value until created
      event.target.value = transaction.category_id;
    } else {
      transaction.category_id = Number(value);
    }
  }

  onTypeChange(transaction: any, event: any) {
    const value = event.target.value;
    transaction.type = value;
  // Resetear categoría al cambiar tipo
  transaction.category_id = 0;

  // Ajustar signo coherente si quieres mantener consistencia visual
  if (transaction.type === 'income' && transaction.amount < 0) {
    transaction.amount = Math.abs(transaction.amount);
  }

  if (transaction.type === 'expense' && transaction.amount > 0) {
    transaction.amount = -Math.abs(transaction.amount);
  }
}


  openCreateCategoryModal(transaction: any) {
    const name = prompt('Nombre de la nueva categoría para: ' + transaction.type);
    if (!name) return;

    const service = transaction.type === 'income' ? this.incomeCategoryService : this.expenseCategoryService;

    const newCategory = {
      name: name,
      description: 'Creada desde importación',
      active: true,
      id: 0 // ID dummy, backend assigns
    };

    service.create(newCategory).subscribe({
      next: (res) => {
        if (res.response) {
          // Recargar listas
          this.loadCategories();
          // Asignar a la transacción actual
          transaction.category_id = res.response.id;
          alert(`Categoría "${name}" creada y asignada.`);
        }
      },
      error: (err) => alert('Error al crear categoría')
    });
  }

  async saveAll() {
    const toSave = this.pendingTransactions.filter(t => t.selected);
    if (toSave.length === 0) {
      alert('No hay transacciones seleccionadas.');
      return;
    }

    if (!confirm(`¿Guardar ${toSave.length} transacciones?`)) return;

    this.loading = true;
    let savedCount = 0;
    let errors = 0;

    // Guardado secuencial para no saturar (o paralelo limitado)
    // Aquí lo hacemos simple: Promise.all
    const promises = toSave.map(t => {
      const payload = {
        id: 0,
        name: t.description || (t.type === 'income' ? 'Ingreso' : 'Gasto'),
        description: t.description,
        amount: t.amount,
        date: t.date,
        currency: CurrencyEnum.Euro,
        user_id: 1, // TODO: Get from auth
        account_id: 1, // TODO: Selectable account
        category_id: t.category_id || 1, // Default fallback
        // Specific fields
        ...(t.type === 'income' ? { source_id: t.source_id } : { place_id: t.place_id })
      };

      const service = t.type === 'income' ? this.incomeService : this.expenseService;
      // @ts-ignore
      return service.create(payload).toPromise()
        .then(() => { savedCount++; })
        .catch(() => { errors++; });
    });

    await Promise.all(promises);

    this.loading = false;
    alert(`Proceso finalizado.\nGuardados: ${savedCount}\nErrores: ${errors}`);

    // Limpiar lista si todo ok
    if (errors === 0) {
      this.pendingTransactions = [];
      this.fileName = '';
    }
  }
}
