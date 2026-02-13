"""Service for Saving implementing CRUD operations."""
from sqlalchemy.orm import Session
from repositories.saving_repository import SavingRepository
from schemas.saving_schema import SavingCreate, SavingRead, SavingUpdate
from models import Saving
from services.base_service import BaseService


class SavingService(BaseService[Saving, SavingRead, SavingCreate, SavingUpdate]):
    """Service for Saving domain logic."""

    def __init__(self, db: Session):
        super().__init__(
            db=db,
            model=Saving,
            repository=SavingRepository(db),
            read_schema=SavingRead
        )
