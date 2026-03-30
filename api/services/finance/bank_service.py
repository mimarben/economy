"""Service for Bank implementing CRUD operations."""
from sqlalchemy.orm import Session
from repositories.finance.bank_repository import BankRepository
from schemas.finance.bank_schema import BankCreate, BankRead, BankUpdate
from models import Bank
from services.core.base_service import BaseService


class BankService(BaseService[Bank, BankRead, BankCreate, BankUpdate]):
    """Service for Bank domain logic."""

    def __init__(self, db: Session):
        super().__init__(
            db=db,
            model=Bank,
            repository=BankRepository(db),
            read_schema=BankRead
        )

    @staticmethod
    def _normalize_cif(cif: str | None) -> str | None:
        if cif is None:
            return None
        return cif.replace(' ', '').upper()

    def create(self, data: BankCreate) -> BankRead:
        cif = self._normalize_cif(data.cif)
        data.cif = cif

        if cif and self.repository.find_by_cif(cif):
            raise ValueError("Bank with this CIF already exists")

        return super().create(data)

    def update(self, id: int, data: BankUpdate) -> BankRead:
        existing = self.repository.get_by_id(id)
        if not existing:
            return None

        if data.cif is not None:
            normalized = self._normalize_cif(data.cif)
            if normalized != existing.cif and self.repository.find_by_cif(normalized):
                raise ValueError("Another bank with this CIF already exists")
            data.cif = normalized

        return super().update(id, data)
