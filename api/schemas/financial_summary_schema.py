from pydantic import BaseModel
from typing import Optional
from datetime import datetime
class FinancialSummaryBase(BaseModel):
    name: str
    date: datetime
    total_income = float
    total_expenses = float
    total_savings = float
    total_investments = float
    net_worth =float

class FinancialSummaryRead(FinancialSummaryBase):
    id: int

    class Config:
        from_attributes = True

class FinancialSummaryCreate(FinancialSummaryBase):
    pass

class FinancialSummaryUpdate(BaseModel):
    name: Optional[str]
    date: Optional[datetime]
    total_income = Optional[float]
    total_expenses = Optional[float]
    total_savings = Optional[float]
    total_investments = Optional[float]
    net_worth =Optional[float]