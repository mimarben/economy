from sqlalchemy import (
    Boolean,
    Column,
    Integer,
    String,
    Numeric,
    Date,
    ForeignKey,
    Enum as SQLEnum,
    UniqueConstraint
)
from sqlalchemy.orm import relationship

from ..core.base import Base, TimestampMixin
from ..core.enums import CurrencyEnum


class Expense(TimestampMixin, Base):
    __tablename__ = 'expenses'
    __table_args__ = (
        UniqueConstraint('account_id', 'dedup_hash', name='uq_expenses_account_dedup_hash'),
    )

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(String)
    amount = Column(Numeric(12, 2), nullable=False)
    date = Column(Date, nullable=False)
    currency = Column(SQLEnum(CurrencyEnum), nullable=False)
    ignore_in_analysis = Column(Boolean, default=False, nullable=False)
    dedup_hash = Column(String(64), nullable=False, index=True)
    is_personal = Column(Boolean, default=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True, index=True)

    # Foreign Keys
    source_id = Column(Integer, ForeignKey('sources.id'), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey('expenses_categories.id'), nullable=False, index=True)
    account_id = Column(Integer, ForeignKey('accounts.id'), nullable=False, index=True)
    card_id = Column(Integer, ForeignKey("cards.id"), nullable=True)
    
    # Relationships
    source = relationship('Source', back_populates='expenses')
    category = relationship('ExpensesCategory', back_populates='expenses')
    account = relationship('Account', back_populates='expenses')
    card = relationship("Card",  back_populates='expenses')
    user = relationship('User', back_populates='expenses')
