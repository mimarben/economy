export interface ClassifyRequest {
  id: number;
  type: 'income' | 'expense' | 'investment';
  description: string;
  amount: number;
}

export interface CategoryRule {
  keywords: string[];
  categoryName: string;
  type: 'expense' | 'income' | 'investment';
}
export interface ClassifyResult {
  id: number;
  category: { 
    id: number; 
    name: string; 
    description?: string,
    suggested_new_category?: string | null; 
  } | null;
}

export interface ClassifyPayload {
  transactions: ClassifyRequest[];
  rules: CategoryRule[];
}
