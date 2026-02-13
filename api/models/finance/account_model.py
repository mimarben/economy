from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from ..core.base import Base


class Account(Base):
    __tablename__ = 'accounts'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(String)
    iban = Column(String, nullable=False)
    balance = Column(Float, nullable=False)
    active = Column(Boolean, default=True, nullable=False)

    # Foreign Keys
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    bank_id = Column(Integer, ForeignKey('banks.id'), nullable=False)

    # Relationships
    users = relationship('User', back_populates='accounts')
    banks = relationship('Bank', back_populates='accounts')
    savings = relationship('Saving', back_populates='accounts')
    investments = relationship('Investment', back_populates='accounts')
    expenses = relationship('Expense', back_populates='accounts')
    incomes = relationship('Income', back_populates='accounts')
