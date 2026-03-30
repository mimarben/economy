from sqlalchemy import Column, Integer, String, Numeric, Boolean, ForeignKey, Enum as SQLEnum, UniqueConstraint
from sqlalchemy.orm import relationship

from ..core.base import Base, TimestampMixin
from ..core.enums import CurrencyEnum

class Account(TimestampMixin, Base):
    __tablename__ = 'accounts'
    __table_args__ = (
        UniqueConstraint('iban', name='uq_accounts_iban'),
    )
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(String)
    iban = Column(String, nullable=True)
    currency = Column(SQLEnum(CurrencyEnum), nullable=False)
    active = Column(Boolean, default=True, nullable=False)
    balance = Column(Numeric(12, 2), nullable=True)
    # Foreign Keys
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    bank_id = Column(Integer, ForeignKey('banks.id'), nullable=False, index=True)

    # Relationships
    user = relationship('User', back_populates='accounts')
    bank = relationship('Bank', back_populates='accounts')
    
    savings = relationship('Saving', back_populates='account')
    investments = relationship('Investment', back_populates='account')
    expenses = relationship('Expense', back_populates='account')
    incomes = relationship('Income', back_populates='account')
