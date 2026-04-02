from sqlalchemy.orm import Session
from models import Card

from schemas.cards.card_schema import CardCreate, CardRead, CardUpdate
from services.core.base_service import BaseService
from repositories.cards.card_repository import CardRepository
class CardService(BaseService[Card, CardRead, CardCreate, CardUpdate]):
     def __init__(self, db: Session):
        repository = CardRepository(db)
        super().__init__(
            db=db,
            model=Card,
            repository=repository,
            read_schema=CardRead
        )