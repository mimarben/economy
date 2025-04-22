from pydantic import BaseModel
from typing import Optional

class PlaceBase(BaseModel):
    name: str
    address: Optional[str] = None
    description: Optional[str] = None
    active: bool = True
class PlaceRead(PlaceBase):
    id: int

    class Config:
        from_attributes = True

class PlaceCreate(PlaceBase):
    pass

class PlaceUpdate(PlaceBase):
    pass


