from sqlalchemy import Column, Integer, String, Date, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship

from ..core.base import Base, TimestampMixin
from ..core.enums import CurrencyEnum


class Investment(TimestampMixin, Base):
    __tablename__ = 'investments'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(String)
    date = Column(Date, nullable=False)
    currency = Column(SQLEnum(CurrencyEnum), nullable=False)

    # Foreign Keys
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    account_id = Column(Integer, ForeignKey('accounts.id'), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey('investments_categories.id'), nullable=False, index=True)

    # Relationships
    user = relationship('User', back_populates='investments')
    account = relationship('Account', back_populates='investments')
    category = relationship('InvestmentsCategory', back_populates='investments')
    investment_logs = relationship('InvestmentLog', back_populates='investment')
