"""Service for SavingLog implementing CRUD operations."""
from sqlalchemy.orm import Session
from repositories.saving_log_repository import SavingLogRepository
from schemas.saving_log_schema import SavingLogCreate, SavingLogRead, SavingLogUpdate
from models.models import SavingLog
from services.base_service import BaseService


class SavingLogService(BaseService[SavingLog, SavingLogRead, SavingLogCreate, SavingLogUpdate]):
    """Service for SavingLog domain logic."""

    def __init__(self, db: Session):
        super().__init__(
            db=db,
            model=SavingLog,
            repository=SavingLogRepository(db),
            read_schema=SavingLogRead
        )
