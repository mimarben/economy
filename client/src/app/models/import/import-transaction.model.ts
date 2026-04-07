export interface ImportTransaction {
  date: string;
  description: string;
  amount: number;
  balance?: number;
  selected: boolean;
  suggestedCategoryId?: number | null;
  suggestedCategoryName?: string | null;
  source_id?: number | null;
  account_id?: number | null;
  card_id?: number | null;
  suggestedSourceId?: number | null;
  suggestedAccountId?: number | null;
  ignore_in_analysis?: boolean;
}
