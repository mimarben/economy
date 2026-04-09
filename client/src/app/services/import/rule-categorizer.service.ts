import { Injectable } from "@angular/core";

import { ImportTransaction } from "@import_models/import-transaction.model";
import { IncomeCategoryBase } from "@incomes_models/IncomeCategoryBase";
import { ExpenseCategoryBase } from "@expenses_models/ExpenseCategoryBase";
import { CategoryRuleService, CategoryRule } from "../category-rule/category-rule.service";
import { firstValueFrom } from "rxjs";

@Injectable({
  providedIn: "root"
})
export class RuleCategorizerService {
  // Cache for rules to avoid multiple API calls
  private rulesCache: CategoryRule[] = [];

  constructor(private categoryRuleService: CategoryRuleService) {
    // Keep local cache in sync with any changes in the service.
    this.categoryRuleService.rules$.subscribe((rules) => {
      this.rulesCache = rules;
      console.log('[RuleCategorizerService] rules$ updated:', this.rulesCache);
    });

    this.loadRulesCache();
  }

  /**
   * Load category rules from the backend and cache them.
   * Called on service initialization and can be manually refreshed.
   */
  async loadRulesCache(): Promise<void> {
    try {
      const rules = await firstValueFrom(this.categoryRuleService.getAllRules());
      this.rulesCache = rules;
      console.log('[RuleCategorizerService] Category rules loaded and cached:', this.rulesCache);
    } catch (error) {
      console.error('[RuleCategorizerService] Failed to load category rules from backend:', error);
      this.rulesCache = [];
    }
  }

  /**
   * Normalize text for matching (remove accents, convert to lowercase).
   */
  normalize(text?: any): string {
    if (!text) return "";

    return String(text)
      .toLowerCase()
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "");
  }

  /**
   * Categorize transactions using backend rules.
   * 
   * Backend will apply rules in priority order and fallback to AI if needed.
   * This service is now mainly for UI display purposes - the actual categorization
   * happens on the backend during import.
   * 
   * However, this method can still be used to suggest categories in the UI.
   */
  categorize(
    transactions: ImportTransaction[],
    incomeCategories: IncomeCategoryBase[],
    expenseCategories: ExpenseCategoryBase[]
  ): ImportTransaction[] {
    // Note: Categorization now happens on the backend during import.
    // This method is also used for UI suggestions (local rule matching) if available.

    return transactions.map((t) => {
      const type = t.amount < 0 ? 'expense' : 'income';
      const { categoryId, ignoreInAnalysis } = this.suggestCategoryAndIgnoreFlag(
        String(t.description || ''),
        type
      );

      if (categoryId) {
        t.suggestedCategoryId = categoryId;

        const matchedCategory = (type === 'expense' ? expenseCategories : incomeCategories)
          .find((c) => c.id === categoryId);

        if (matchedCategory) {
          t.suggestedCategoryName = (matchedCategory as any).name || null;
        }
      }

      // Apply ignore_in_analysis flag from rules
      t.ignore_in_analysis = ignoreInAnalysis;

      return t;
    });
  }

  /**
   * Apply rules locally for UI suggestions (optional).
   * This can be used to provide real-time suggestions in import dialogs.
   */
  suggestCategory(
    description: string,
    transactionType: 'expense' | 'income'
  ): number | null {
    if (!description || !this.rulesCache.length) {
      return null;
    }

    const rules = this.rulesCache
      .filter(r => r.type === transactionType && r.is_active)
      .sort((a, b) => b.priority - a.priority);

    for (const rule of rules) {
      try {
        const regex = new RegExp(rule.pattern, 'i');
        if (regex.test(description)) {
          return rule.category_id;
        }
      } catch (e) {
        console.error(`Invalid regex in rule ${rule.id}:`, e);
      }
    }

    return null;
  }

  /**
   * Suggest category and ignore_in_analysis flag from rules.
   * Returns both the category_id and whether the transaction should be ignored in analysis.
   */
  suggestCategoryAndIgnoreFlag(
    description: string,
    transactionType: 'expense' | 'income'
  ): { categoryId: number | null; ignoreInAnalysis: boolean } {
    if (!description || !this.rulesCache.length) {
      return { categoryId: null, ignoreInAnalysis: false };
    }

    const rules = this.rulesCache
      .filter(r => r.type === transactionType && r.is_active)
      .sort((a, b) => b.priority - a.priority);

    for (const rule of rules) {
      try {
        const regex = new RegExp(rule.pattern, 'i');
        if (regex.test(description)) {
          return {
            categoryId: rule.category_id,
            ignoreInAnalysis: rule.ignore_in_analysis ?? false
          };
        }
      } catch (e) {
        console.error(`Invalid regex in rule ${rule.id}:`, e);
      }
    }

    return { categoryId: null, ignoreInAnalysis: false };
  }

  /**
   * Manually refresh the rules cache.
   */
  async refreshRules(): Promise<void> {
    await this.loadRulesCache();
  }

}