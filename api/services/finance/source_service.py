"""Service for Source implementing CRUD operations."""
from sqlalchemy.orm import Session
from repositories.finance.source_repository import SourceRepository
from schemas.finance.source_schema import SourceCreate, SourceRead, SourceUpdate
from models import Source
from services.core.base_service import BaseService


class SourceService(BaseService[Source, SourceRead, SourceCreate, SourceUpdate]):
    """Service for Source domain logic."""

    def __init__(self, db: Session):
        super().__init__(
            db=db,
            model=Source,
            repository=SourceRepository(db),
            read_schema=SourceRead
        )

    def suggest_source(self, category_id: int, transaction_type: str):
        """Return suggested source for given category/transaction type."""
        # Default behavior: choose active source by source_type if available
        # transaction_type expected: expense|income|investment
        source = self.repository.get_active_by_type(transaction_type)

        if source:
            return source

        # Fallback to first active source
        return self.repository.get_first_active()
