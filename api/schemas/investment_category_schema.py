from pydantic import BaseModel
from typing import Optional

class InvestmentCategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    active: bool = True
class InvestmentCategoryRead(InvestmentCategoryBase):
    id: int

    class Config:
        from_attributes = True

class InvestmentCategoryCreate(InvestmentCategoryBase):
    pass

class InvestmentCategoryUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]
    active: Optional[bool]