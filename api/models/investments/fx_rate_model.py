import enum

from sqlalchemy import Column, Integer, String, Numeric, Enum as SQLEnum, UniqueConstraint, Index, DateTime
from sqlalchemy.orm import relationship

from ..core.base import Base, TimestampMixin
from ..core.enums import CurrencyEnum


class FXRate(TimestampMixin, Base):
    __tablename__ = 'fx_rates'

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    base_currency = Column(SQLEnum(CurrencyEnum), nullable=False)
    target_currency = Column(SQLEnum(CurrencyEnum), nullable=False)
    rate = Column(Numeric(18, 10), nullable=False)
    source = Column(String(32), nullable=False)  # 'ecb', 'eulerpool', etc.
    published_at = Column(DateTime, nullable=False)  # When the rate was published

    __table_args__ = (
        # Unique constraint over (base_currency, target_currency, source, published_at)
        UniqueConstraint(
            'base_currency', 'target_currency', 'source', 'published_at',
            name='uq_fx_rate_unique'
        ),
        # Index for common lookups
        Index('ix_fx_rate_base_target', 'base_currency', 'target_currency'),
    )
