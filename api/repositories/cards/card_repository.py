"""Repository for Card entity following segregated interfaces."""
from repositories.core.base_repository import BaseRepository
from models import Card


class CardRepository(BaseRepository[Card]):
    """Repository for Card with custom queries."""

    def __init__(self, db):
        super().__init__(db, Card)