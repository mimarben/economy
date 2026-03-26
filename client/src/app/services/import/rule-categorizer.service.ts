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
    this.loadRulesCache();
  }

  /**
   * Load category rules from the backend and cache them.
   * Called on service initialization and can be manually refreshed.
   */
  async loadRulesCache(): Promise<void> {
    try {
      this.rulesCache = await firstValueFrom(this.categoryRuleService.getAllRules());
    } catch (error) {
      console.error('Failed to load category rules from backend:', error);
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
    // This method is kept for backward compatibility with the UI flow,
    // but the actual categorization is delegated to the CategorizationService on the backend.
    
    return transactions.map(t => {
      // For now, return transactions as-is. The backend will handle categorization.
      // If you need client-side suggestion logic, implement it here using this.rulesCache
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
   * Manually refresh the rules cache.
   */
  async refreshRules(): Promise<void> {
    await this.loadRulesCache();
  }

}