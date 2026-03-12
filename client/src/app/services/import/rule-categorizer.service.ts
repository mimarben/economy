import { Injectable } from "@angular/core";

import { CATEGORY_RULES } from "@app/core/import/category-rules.const";
import { ImportTransaction } from "@app/models/import/import-transaction.model";
import { IncomeCategoryBase } from "@app/models/incomes/IncomeCategoryBase";
import { ExpenseCategoryBase } from "@app/models/expenses/ExpenseCategoryBase";

@Injectable({
  providedIn: "root"
})
export class RuleCategorizerService {

  normalize(text?: any): string {

    if (!text) return "";

    return String(text)
      .toLowerCase()
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "");

  }

  categorize(
    transactions: ImportTransaction[],
    incomeCategories: IncomeCategoryBase[],
    expenseCategories: ExpenseCategoryBase[]
  ): ImportTransaction[] {

    return transactions.map(t => {

      const description = this.normalize(t.description);

      for (const rule of CATEGORY_RULES) {

        const match = rule.keywords.some(keyword =>
          description.includes(this.normalize(keyword))
        );

        if (!match) continue;

        // decidir tipo por importe
        const categories =
          t.amount < 0 ? expenseCategories : incomeCategories;

        const category = categories.find(
          c => c.name === rule.categoryName
        );

        if (category) {
          t.suggestedCategoryId = category.id;
        }

        break;
      }

      return t;

    });

  }

}