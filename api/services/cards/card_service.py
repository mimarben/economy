from sqlalchemy.orm import Session
from models.cards.card_model import Card
from schemas.cards.card_schema import CardCreate, CardRead, CardUpdate


class CardService:

    def __init__(self, db: Session):
        self.db = db       
        
def create(self, data: CardCreate) -> CardRead:
    card = Card(**data.model_dump())
    self.db.add(card)
    self.db.commit()
    self.db.refresh(card)
    return CardRead.model_validate(card)


def get_by_id(self, card_id: int):
    return self.db.query(Card).filter(Card.id == card_id).first()


def get_all(self):
    return self.db.query(Card).all()

def get_by_account(self, account_id: int):
    return (
        self.db.query(Card)
        .filter(Card.account_id == account_id)
        .all()
    )
    
def update(self, card_id: int, data: CardUpdate):
    card = self.get_by_id(card_id)
    if not card:
        return None

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(card, key, value)

    self.db.commit()
    self.db.refresh(card)
    return CardRead.model_validate(card)


def delete(self, card_id: int):
    card = self.get_by_id(card_id)
    if not card:
        return False

    self.db.delete(card)
    self.db.commit()
    return True