from pydantic import BaseModel
from typing import Optional
from utils.schema_exporter import export_schema  # si guardas la función en otro archivo
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

export_schema(InvestmentCategoryBase)
