from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property

from ..core.base import Base, TimestampMixin


class MarketQuote(TimestampMixin, Base):
    """Cached market quote for an ISIN (fund, ETF or stock).

    Populated by the market data providers (Yahoo Finance, ...) through
    MarketQuoteService. `fetched_at` drives the cache TTL: stale rows are
    refreshed on demand instead of hammering the external API.
    
    Note: quoted_at stores the timestamp of the quote itself (EOD/NAV time),
    while fetched_at stores when we retrieved it.
    """

    __tablename__ = 'market_quotes'
    __table_args__ = (
        # Keep the original ISIN uniqueness for backward compatibility
        UniqueConstraint('isin', name='uq_market_quotes_isin'),
    )

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    isin = Column(String(12), nullable=True, index=True)  # nullable for instruments without ISIN
    symbol = Column(String(32), nullable=True)
    name = Column(String(255), nullable=True)
    instrument_type = Column(String(32), nullable=True)
    currency = Column(String(8), nullable=True)
    last_price = Column(Numeric(18, 6), nullable=True)
    previous_close = Column(Numeric(18, 6), nullable=True)
    source = Column(String(20), nullable=True)
    fetched_at = Column(DateTime, nullable=False)
    
    # New columns for quote metadata
    quoted_at = Column(DateTime, nullable=True)  # When the quote was actually valid (EOD/NAV time)
    price_type = Column(String(16), nullable=True)  # 'EOD', 'DELAYED', 'REAL_TIME', 'NAV'
    
    # Relationship to instruments (new: can quote instruments without ISIN)
    instrument_id = Column(Integer, ForeignKey('instruments.id'), nullable=True)
    
    # Relationships
    instrument = relationship('Instrument', back_populates='market_quotes')
