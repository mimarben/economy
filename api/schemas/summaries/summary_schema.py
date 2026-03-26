"""Summary schemas for API requests and responses."""
from typing import Dict, List, Optional
from datetime import date
from pydantic import BaseModel, Field


class TotalByCategory(BaseModel):
    """Total amount aggregated by category."""
    category_id: int
    category_name: str
    type: str  # 'expense' | 'income' | 'investment'
    total: float


class TotalOverTime(BaseModel):
    """Total amount aggregated by date."""
    date: date
    expense: float = 0.0
    income: float = 0.0
    investment: float = 0.0
    net: float = 0.0  # income - expense


class IncomeVsExpense(BaseModel):
    """Income vs Expense comparison."""
    total_income: float
    total_expense: float
    net: float
    count_transactions: int


class SummaryResponse(BaseModel):
    """Complete summary response with aggregated data."""
    period_start: date
    period_end: date
    totals_by_category: List[TotalByCategory]
    totals_over_time: List[TotalOverTime]
    income_vs_expense: IncomeVsExpense

    class Config:
        from_attributes = True
