"""Service for ImportOrigin implementing CRUD operations."""

from sqlalchemy.orm import Session

from models.imports import ImportOrigin
from repositories.imports.import_origin_repository import ImportOriginRepository
from schemas.imports.import_origin_schema import (
    ImportOriginCreate,
    ImportOriginRead,
    ImportOriginUpdate,
)

from services.core.base_service import BaseService


class ImportOriginService(
    BaseService[
        ImportOrigin,
        ImportOriginRead,
        ImportOriginCreate,
        ImportOriginUpdate
    ]
):
    """Service for ImportOrigin domain logic."""

    def __init__(self, db: Session):
        super().__init__(
            db=db,
            model=ImportOrigin,
            repository=ImportOriginRepository(db),
            read_schema=ImportOriginRead
        )

    # 🔥 aquí puedes añadir lógica futura
    def get_by_code(self, code: str):
        return self.repository.get_by_code(code)