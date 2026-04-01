from typing import List, Optional
from pydantic import BaseModel, Field




class ExpenseImportCreate(BaseModel):
    """Schema for expense import - category_id is optional (will be auto-categorized)."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=500)
    amount: float = Field(..., gt=0)
    date: str  # Import accepts string, parsed as datetime
    currency: str
    user_id: int = Field(..., gt=0)
    source_id: int = Field(..., gt=0)
    category_id: Optional[int] = Field(None, gt=0)  # Optional - will be auto-categorized
    account_id: Optional[int] = Field(None, gt=0)


class IncomeImportCreate(BaseModel):
    """Schema for income import - category_id is optional (will be auto-categorized)."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=500)
    amount: float = Field(..., gt=0)
    date: str  # Import accepts string, parsed as datetime
    currency: str
    source_id: int = Field(..., gt=0)
    category_id: Optional[int] = Field(None, gt=0)  # Optional - will be auto-categorized
    account_id: Optional[int] = Field(None, gt=0)


class BulkImportRequest(BaseModel):
    """Schema for bulk import of incomes and expenses atomically."""
    expenses: List[ExpenseImportCreate] = Field(default_factory=list)
    incomes: List[IncomeImportCreate] = Field(default_factory=list)
    # Option: auto_categorize transactions if category_id is null
    auto_categorize: bool = Field(default=True)