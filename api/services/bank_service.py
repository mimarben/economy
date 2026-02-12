"""Service for Bank implementing CRUD operations."""
from sqlalchemy.orm import Session
from repositories.bank_repository import BankRepository
from schemas.bank_schema import BankCreate, BankRead, BankUpdate
from models.models import Bank
from services.base_service import BaseService


class BankService(BaseService[Bank, BankRead, BankCreate, BankUpdate]):
    """Service for Bank domain logic."""

    def __init__(self, db: Session):
        super().__init__(
            db=db,
            model=Bank,
            repository=BankRepository(db),
            read_schema=BankRead
        )
