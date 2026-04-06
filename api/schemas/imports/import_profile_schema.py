from pydantic import BaseModel, Field, field_validator
from typing import Dict, List, Optional
from schemas.core.audit_schema import AuditFields


class ImportProfileBase(BaseModel):
    origin_id: int = Field(
        ...,
        gt=0,
        json_schema_extra={
            "ui_type": "select",
            "relation": "origin",
        },
    )
    name: str
    header_row_guess: int = 1
    columns: Dict[str, List[str]]
    active: bool = True
    
    @field_validator("columns")
    @classmethod
    def validate_columns(cls, v):
        if not v:
            raise ValueError("columns cannot be empty")

        for key, values in v.items():
            if not isinstance(values, list) or not values:
                raise ValueError(f"{key} must have at least one alias")
        return v

class ImportProfileRead(ImportProfileBase, AuditFields):
    id: int

    class Config:
        from_attributes = True

class ImportProfileCreate(ImportProfileBase):
    pass

class ImportProfileUpdate(BaseModel):
    origin_id: int
    name: Optional[str]
    header_row_guess: Optional[int]
    columns: Optional[Dict[str, List[str]]]
    active: Optional[bool]
