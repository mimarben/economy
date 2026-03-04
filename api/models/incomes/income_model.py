from sqlalchemy import Column, Integer, String, Numeric, Date, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship

from ..core.base import Base, TimestampMixin
from ..core.enums import CurrencyEnum


class Income(TimestampMixin, Base):
    __tablename__ = 'incomes'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(String)
    amount = Column(Numeric(12, 2), nullable=False)
    date = Column(Date, nullable=False)
    currency = Column(SQLEnum(CurrencyEnum), nullable=False)

    # Foreign Keys
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    source_id = Column(Integer, ForeignKey('sources.id'), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey('incomes_categories.id'), nullable=False, index=True)
    account_id = Column(Integer, ForeignKey('accounts.id'), nullable=True, index=True)

    # Relationships
    user = relationship('User', back_populates='incomes')
    source = relationship('Source', back_populates='incomes')
    category = relationship('IncomesCategory', back_populates='incomes')
    account = relationship('Account', back_populates='incomes')
