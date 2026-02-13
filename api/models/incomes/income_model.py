from sqlalchemy import Column, Integer, String, Float, Date, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship

from ..core.base import Base
from ..core.enums import CurrencyEnum


class Income(Base):
    __tablename__ = 'incomes'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(String)
    amount = Column(Float, nullable=False)
    date = Column(Date, nullable=False)
    currency = Column(SQLEnum(CurrencyEnum), nullable=False)

    # Foreign Keys
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    source_id = Column(Integer, ForeignKey('sources.id'), nullable=False)
    category_id = Column(Integer, ForeignKey('incomes_categories.id'), nullable=False)
    account_id = Column(Integer, ForeignKey('accounts.id'), nullable=True)

    # Relationships
    users = relationship('User', back_populates='incomes')
    sources = relationship('Source', back_populates='incomes')
    categories = relationship('IncomesCategory', back_populates='incomes')
    accounts = relationship('Account', back_populates='incomes')
