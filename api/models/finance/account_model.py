from sqlalchemy import Column, Integer, String, Numeric, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from ..core.base import Base, TimestampMixin


class Account(TimestampMixin, Base):
    __tablename__ = 'accounts'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(String)
    iban = Column(String, nullable=False)
    balance = Column(Numeric(12, 2), nullable=False)
    active = Column(Boolean, default=True, nullable=False)

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
