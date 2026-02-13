"""Service for Source implementing CRUD operations."""
from sqlalchemy.orm import Session
from repositories.source_repository import SourceRepository
from schemas.source_schema import SourceCreate, SourceRead, SourceUpdate
from models import Source
from services.base_service import BaseService


class SourceService(BaseService[Source, SourceRead, SourceCreate, SourceUpdate]):
    """Service for Source domain logic."""

    def __init__(self, db: Session):
        super().__init__(
            db=db,
            model=Source,
            repository=SourceRepository(db),
            read_schema=SourceRead
        )
