from sqlalchemy import Column, Integer, String, Numeric, Date, ForeignKey, Enum as SQLEnum, UniqueConstraint, Index
from sqlalchemy.orm import relationship

from ..core.base import Base, TimestampMixin
from ..core.enums import CurrencyEnum


class Investment(TimestampMixin, Base):
    __tablename__ = 'investments'
    __table_args__ = (
        UniqueConstraint('account_id', 'dedup_hash', name='uq_investments_account_dedup_hash'),
        # Index for performance on instrument_id lookups
        Index('ix_investments_instrument_id', 'instrument_id'),
    )

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    description = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    currency = Column(SQLEnum(CurrencyEnum), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    dedup_hash = Column(String(64), nullable=False, index=True)
    isin = Column(String(12), nullable=True, index=True)  # legacy field, dual-write transition
    
    # New columns for better instrumentation and traceability
    instrument_id = Column(Integer, ForeignKey('instruments.id'), nullable=True)
    source_id = Column(Integer, ForeignKey('sources.id'), nullable=True)  # for import reconciliation

    # Foreign Keys
    account_id = Column(Integer, ForeignKey('accounts.id'), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey('investments_categories.id'), nullable=False, index=True)

    # Relationships
    account = relationship('Account', back_populates='investments')
    category = relationship('InvestmentsCategory', back_populates='investments')
    instrument = relationship('Instrument', back_populates='investments')
    source = relationship('Source', back_populates='investments')
    investment_logs = relationship('InvestmentLog', back_populates='investment')
