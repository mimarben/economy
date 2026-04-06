"""Service for ImportOrigin implementing CRUD operations."""

from sqlalchemy.orm import Session

from models.imports import ImportProfile
from repositories.imports.import_profile_repository import ImportProfileRepository
from schemas.imports.import_profile_schema import (
    ImportProfileCreate,
    ImportProfileRead,
    ImportProfileUpdate,
)

from services.core.base_service import BaseService


class ImportProfileService(
    BaseService[
        ImportProfile,
        ImportProfileRead,
        ImportProfileCreate,
        ImportProfileUpdate
    ]
):
    """Service for ImportProfile domain logic."""

    def __init__(self, db: Session):
        super().__init__(
            db=db,
            model=ImportProfile,
            repository=ImportProfileRepository(db),
            read_schema=ImportProfileRead
        )

    # 🔥 aquí puedes añadir lógica futura
    def get_by_code(self, code: str):
        return self.repository.get_by_code(code)