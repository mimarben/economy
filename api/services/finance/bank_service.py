"""Service for Bank implementing CRUD operations."""
from sqlalchemy.orm import Session
from repositories.finance.bank_repository import BankRepository
from schemas.finance.bank_schema import BankCreate, BankRead, BankUpdate
from models import Bank
from services.core.base_service import BaseService
from core.exceptions import ValidationError


class BankService(BaseService[Bank, BankRead, BankCreate, BankUpdate]):
    """Service for Bank domain logic."""

    def __init__(self, db: Session):
        super().__init__(
            db=db,
            model=Bank,
            repository=BankRepository(db),
            read_schema=BankRead
        )

    def create(self, obj_in: BankCreate) -> Bank:
        existing = self.repository.find_by_cif(obj_in.cif)
        if existing:
            raise ValidationError("Bank with this CIF already exists")
        return super().create(obj_in)

    def update(self, db_obj: Bank, obj_in: BankUpdate) -> Bank:
        if obj_in.cif and obj_in.cif != db_obj.cif:
            existing = self.repository.find_by_cif(obj_in.cif)
            if existing and existing.id != db_obj.id:
                raise ValidationError("Bank with this CIF already exists")
        return super().update(db_obj, obj_in)

