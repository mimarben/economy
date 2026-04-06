from sqlalchemy import Boolean, Column, Integer
from sqlalchemy import  String,  ForeignKey, Enum as SQLEnum, UniqueConstraint
from sqlalchemy.orm import relationship

from ..core.base import Base, TimestampMixin
from ..core.enums import  CardTypeEnum


class Card(TimestampMixin, Base):
    __tablename__ = "cards"
    __table_args__ = (
    UniqueConstraint('account_id', 'name', 'last4', name='uq_card_account_last4'),
    )
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    last4 = Column(String(4))
    type = Column(SQLEnum(CardTypeEnum), nullable=False)    
    active = Column(Boolean, default=True, nullable=False)
    
    # Foreign Keys
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    import_origin_id = Column(Integer, ForeignKey("import_origins.id"))
    # relaciones
    expenses = relationship("Expense", back_populates="card")
    account = relationship("Account", back_populates="cards") 
    import_origin = relationship("ImportOrigin", back_populates="cards")
