from sqlalchemy import Column, Integer, Numeric, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship

from ..core.base import Base, TimestampMixin


class MarketQuoteHistory(TimestampMixin, Base):
    """Historical market quotes for instruments."""
    __tablename__ = 'market_quote_history'

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    instrument_id = Column(Integer, ForeignKey('instruments.id', ondelete='CASCADE'), nullable=False)
    price = Column(Numeric(18, 10), nullable=False)
    quoted_at = Column(DateTime, nullable=False)  # When the quote was actually valid (EOD/NAV time)
    price_type = Column(String(16), nullable=True)  # 'EOD', 'DELAYED', 'REAL_TIME', 'NAV'
    source = Column(String(32), nullable=True)  # 'ecb', 'eulerpool', 'yahoo', etc.

    # Relationships
    instrument = relationship('Instrument', back_populates='market_quote_history')
