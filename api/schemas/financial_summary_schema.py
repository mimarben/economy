from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from utils.schema_exporter import export_schema  # si guardas la función en otro archivo
class FinancialSummaryBase(BaseModel):
    name: str
    date: datetime
    total_income: float
    total_expenses: float
    total_savings: float
    total_investments:float
    net_worth:float
    user_id: int= Field(..., gt=0)
    household_id: int= Field(..., gt=0)

class FinancialSummaryRead(FinancialSummaryBase):
    id: int
    class Config:
        from_attributes = True

class FinancialSummaryCreate(FinancialSummaryBase):
    pass

class FinancialSummaryUpdate(BaseModel):
    name: Optional[str]
    date: Optional[datetime]
    total_income: Optional[float]
    total_expenses: Optional[float]
    total_savings: Optional[float]
    total_investments: Optional[float]
    net_worth: Optional[float]
    user_id: Optional[int]
    household_id: Optional[int]

export_schema(FinancialSummaryBase)
