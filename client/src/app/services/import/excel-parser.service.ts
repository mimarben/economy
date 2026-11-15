import { Injectable } from '@angular/core';
import { UtilsService } from '@utils/utils.service';
import { ImportTransaction } from '@import_models/import-transaction.model';
import { ImportProfileBase as ImportProfile } from '@app/models/import/import-profileBase';
import { AccountBase as Account } from '@finance_models/AccountBase';
import { CardBase as Card } from '@cards_models/CardBase';
import { CurrencyEnum } from '@app/core/const/Currency.enum';

export type TransactionType = 'expense' | 'income';

/** Contextual selections that influence how rows map to ImportTransaction. */
export interface ExcelParseContext {
  selectedAccount?: Account | null;
  selectedCard?: Card | null;
  selectedUserId?: number | null;
}

export interface ExcelParseResult {
  /** Header row (trimmed, normalized length preserved). */
  headers: string[];
  /** Data rows (everything after the header row). */
  dataRows: any[];
  /** Mapped transactions (rows with a non-zero amount only). */
  transactions: ImportTransaction[];
  /** Account/card holder name found in the metadata rows, when present. */
  titularName: string | null;
  /** Detected column indices (-1 when not found). */
  indices: {
    date: number;
    description: number;
    amount: number;
    balance: number;
  };
}

/**
 * Pure Excel-parsing logic extracted from ExcelImportComponent.
 *
 * Responsibilities (UI-agnostic, no I/O):
 *  - detect header/data rows from a profile's `header_row_guess`
 *  - detect date/description/amount/balance columns from a profile's keyword map
 *  - drop rows without a usable amount
 *  - map each valid row to an ImportTransaction (date/amount/currency/flags)
 *
 * Categorization and source suggestion stay in the component / other services.
 */
@Injectable({
  providedIn: 'root',
})
export class ExcelParserService {
  constructor(private utilsService: UtilsService) {}

  /** Infer transaction type from the amount sign (negative = expense). */
  inferTransactionType(amount: number): TransactionType {
    return amount < 0 ? 'expense' : 'income';
  }

  /** Index of the first header containing any of the keywords (normalized match). */
  findColumnIndex(headers: string[], keywords: string[]): number {
    return headers.findIndex((h) => {
      if (!h) return false;
      const header = this.utilsService.normalize(String(h));
      return keywords.some((k) => header.includes(k));
    });
  }

  /**
   * Extract the account/card holder name from the metadata rows above the
   * header (e.g. Pass statements: row 3 has label "Nombre Apellidos" and the
   * holder's real name in the cell to its right). Returns null when absent.
   */
  extractTitularName(rows: any[][], headerIndex: number): string | null {
    for (let r = 0; r < headerIndex; r++) {
      const row = rows[r];
      if (!Array.isArray(row)) continue;
      for (let c = 0; c < row.length - 1; c++) {
        const label = String(row[c] ?? '').trim();
        if (/^nombre/i.test(label)) {
          for (let k = c + 1; k < row.length; k++) {
            const value = String(row[k] ?? '').trim();
            // skip masked card numbers (**** **** ******1135) and empties
            if (value && !/^\*+/.test(value)) {
              return value;
            }
          }
        }
      }
    }
    return null;
  }

  /**
   * Parse raw sheet rows into ImportTransaction[] using the profile's column map.
   * Returns null when the date/description/amount columns cannot be detected.
   */
  parse(
    rows: any[][],
    profile: ImportProfile,
    ctx: ExcelParseContext = {},
  ): ExcelParseResult | null {
    const headerRow = profile.header_row_guess ?? 1;
    const headerIndex = headerRow - 1;

    const headers: string[] = (rows[headerIndex] as any[]).map((h) =>
      h ? String(h).trim() : '',
    );
    // Bank .xls exports often carry formatting on all 65k rows of the legacy
    // sheet, so sheet_to_json returns tens of thousands of ghost empty rows.
    // Drop rows without a single non-empty cell before mapping/counting.
    const isEmptyRow = (row: any): boolean =>
      !Array.isArray(row) ||
      row.every((cell) => cell === null || cell === undefined || String(cell).trim() === '');
    const dataRows: any[] = rows.slice(headerIndex + 1).filter((row) => !isEmptyRow(row));

    const dateIndex = this.findColumnIndex(headers, profile.columns['date'] ?? []);
    const descriptionIndex = this.findColumnIndex(headers, profile.columns['description'] ?? []);
    const amountIndex = this.findColumnIndex(headers, profile.columns['amount'] ?? []);
    const balanceIndex = this.findColumnIndex(headers, profile.columns['balance'] ?? []);

    if (dateIndex === -1 || descriptionIndex === -1 || amountIndex === -1) {
      return null;
    }

    const validRows = dataRows.filter((row) => {
      const amount = this.utilsService.parseAmount(row[amountIndex]);
      // Drop rows without amount
      if (amount === null || amount === undefined || isNaN(amount) || amount === 0) {
        return false;
      }
      return true;
    });

    const transactions: ImportTransaction[] = validRows.map((row) => {
      // Card statements hold the REAL purchases (analyzable, tied to the card).
      // The duplicate side of this flow — the monthly card payment charge in the
      // bank statement ("Recibo FINANCIERA CARREFOUR") — is already flagged
      // ignore_in_analysis by its category rule, so no auto-discard here.
      // parseAmount() returns 0 for missing cells; without a balance column
      // (index -1) the value must stay null or the balance-chain check in the
      // preview flags every row as a mismatch.
      const rawBalance = balanceIndex >= 0 ? row[balanceIndex] : undefined;
      const balance =
        rawBalance === null || rawBalance === undefined || String(rawBalance).trim() === ''
          ? undefined
          : this.utilsService.parseAmount(rawBalance);
      return {
        date: this.utilsService.toIsoDate(row[dateIndex]),
        description: row[descriptionIndex],
        amount: this.utilsService.parseAmount(row[amountIndex]),
        balance,
        suggestedCategoryId: null,
        suggestedCategoryName: null,
        source_id: null,
        account_id: ctx.selectedAccount?.id ?? null,
        suggestedSourceId: null,
        suggestedAccountId: ctx.selectedAccount?.id ?? null,
        card_id: ctx.selectedCard?.id ?? null,
        currency: CurrencyEnum.EUR,
        ignore_in_analysis: false,
        selected: true,
        user_id: ctx.selectedUserId ?? null,
      };
    });

    return {
      headers,
      dataRows,
      transactions,
      titularName: this.extractTitularName(rows, headerIndex),
      indices: {
        date: dateIndex,
        description: descriptionIndex,
        amount: amountIndex,
        balance: balanceIndex,
      },
    };
  }
}
