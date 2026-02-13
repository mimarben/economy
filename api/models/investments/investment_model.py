from sqlalchemy import Column, Integer, String, Float, Date, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship

from ..core.base import Base
from ..core.enums import CurrencyEnum


class Investment(Base):
    __tablename__ = 'investments'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(String)
    date = Column(Date, nullable=False)
    currency = Column(SQLEnum(CurrencyEnum), nullable=False)

    # Foreign Keys
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    account_id = Column(Integer, ForeignKey('accounts.id'), nullable=False)
    category_id = Column(Integer, ForeignKey('investments_categories.id'), nullable=False)

    # Relationships
    users = relationship('User', back_populates='investments')
    accounts = relationship('Account', back_populates='investments')
    categories = relationship('InvestmentsCategory', back_populates='investments')
    investment_logs = relationship('InvestmentLog', back_populates='investments')
