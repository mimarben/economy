from sqlalchemy import Column, Integer, String, Numeric, Date, ForeignKey, Enum as SQLEnum, UniqueConstraint
from sqlalchemy.orm import relationship

from ..core.base import Base, TimestampMixin
from ..core.enums import CurrencyEnum


class Investment(TimestampMixin, Base):
    __tablename__ = 'investments'
    __table_args__ = (
        UniqueConstraint('account_id', 'dedup_hash', name='uq_investments_account_dedup_hash'),
    )

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    description = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    currency = Column(SQLEnum(CurrencyEnum), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    dedup_hash = Column(String(64), nullable=False, index=True)
    # Foreign Keys
    #user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    account_id = Column(Integer, ForeignKey('accounts.id'), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey('investments_categories.id'), nullable=False, index=True)

    # Relationships
    #user = relationship('User', back_populates='investments')
    account = relationship('Account', back_populates='investments')
    category = relationship('InvestmentsCategory', back_populates='investments')
    investment_logs = relationship('InvestmentLog', back_populates='investment')
