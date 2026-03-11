from sqlalchemy import Column, Integer, String, Numeric, Date, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship

from ..core.base import Base, TimestampMixin
from ..core.enums import CurrencyEnum


class Expense(TimestampMixin, Base):
    __tablename__ = 'expenses'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(String)
    amount = Column(Numeric(12, 2), nullable=False)
    date = Column(Date, nullable=False)
    currency = Column(SQLEnum(CurrencyEnum), nullable=False)

    # Foreign Keys
    #user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    source_id = Column(Integer, ForeignKey('sources.id'), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey('expenses_categories.id'), nullable=False, index=True)
    account_id = Column(Integer, ForeignKey('accounts.id'), nullable=False, index=True)

    # Relationships
    #user = relationship('User', back_populates='expenses')
    source = relationship('Source', back_populates='expenses')
    category = relationship('ExpensesCategory', back_populates='expenses')
    account = relationship('Account', back_populates='expenses')
