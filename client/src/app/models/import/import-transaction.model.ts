export interface ImportTransaction {

  date: string;

  description: string;

  amount: number;

  balance?: number;
  
  selected: boolean;

  suggestedCategoryId?: number | null;
  
  suggestedCategoryName?: string | null; // ← añade esto

}