from typing import List
from datetime import date as DateType
from pydantic import BaseModel, Field


class TotalByCategory(BaseModel):
    """Total amount aggregated by category."""
    category_id: int = Field(...)
    category_name: str = Field(...)
    type: str = Field(...)  # 'expense' | 'income' | 'investment'
    total: float = Field(...)


class TotalOverTime(BaseModel):
    """Total amount aggregated by date."""
    date: DateType = Field(...)
    expense: float = Field(default=0.0)
    income: float = Field(default=0.0)
    investment: float = Field(default=0.0)
    net: float = Field(default=0.0)  # income - expense


class IncomeVsExpense(BaseModel):
    """Income vs Expense comparison."""
    total_income: float = Field(...)
    total_expense: float = Field(...)
    net: float = Field(...)
    count_transactions: int = Field(...)

class SummaryResponse(BaseModel):
    """Complete summary response with aggregated data."""
    period_start: DateType = Field(...)
    period_end: DateType = Field(...)
    totals_by_category: List[TotalByCategory] = Field(...)
    totals_over_time: List[TotalOverTime] = Field(...)
    income_vs_expense: IncomeVsExpense = Field(...)

    class Config:
        from_attributes = True
