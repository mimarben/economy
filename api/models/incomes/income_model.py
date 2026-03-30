from sqlalchemy import Column, Integer, String, Numeric, Date, ForeignKey, Enum as SQLEnum, UniqueConstraint
from sqlalchemy.orm import relationship

from ..core.base import Base, TimestampMixin
from ..core.enums import CurrencyEnum


class Income(TimestampMixin, Base):
    __tablename__ = 'incomes'
    __table_args__ = (
        UniqueConstraint('account_id', 'dedup_hash', name='uq_incomes_account_dedup_hash'),
    )

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    description = Column(String, nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    date = Column(Date, nullable=False)
    currency = Column(SQLEnum(CurrencyEnum), nullable=False)
    dedup_hash = Column(String(64), nullable=False, index=True)

    # Foreign Keys
    source_id = Column(Integer, ForeignKey('sources.id'), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey('incomes_categories.id'), nullable=False, index=True)
    account_id = Column(Integer, ForeignKey('accounts.id'), nullable=False, index=True)

    # Relationships
    source = relationship('Source', back_populates='incomes')
    category = relationship('IncomesCategory', back_populates='incomes')
    account = relationship('Account', back_populates='incomes')
