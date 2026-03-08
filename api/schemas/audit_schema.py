from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class AuditFields(BaseModel):
    """Readonly audit fields returned by API entities."""

    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
