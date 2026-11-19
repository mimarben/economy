from sqlalchemy import Column, Integer, String, Numeric, DateTime, UniqueConstraint

from ..core.base import Base, TimestampMixin


class MarketQuote(TimestampMixin, Base):
    """Cached market quote for an ISIN (fund, ETF or stock).

    Populated by the market data providers (Yahoo Finance, ...) through
    MarketQuoteService. `fetched_at` drives the cache TTL: stale rows are
    refreshed on demand instead of hammering the external API.
    """

    __tablename__ = 'market_quotes'
    __table_args__ = (
        UniqueConstraint('isin', name='uq_market_quotes_isin'),
    )

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    isin = Column(String(12), nullable=False, index=True)
    symbol = Column(String(32), nullable=True)
    name = Column(String(255), nullable=True)
    instrument_type = Column(String(32), nullable=True)
    currency = Column(String(8), nullable=True)
    last_price = Column(Numeric(18, 6), nullable=True)
    previous_close = Column(Numeric(18, 6), nullable=True)
    source = Column(String(20), nullable=True)
    fetched_at = Column(DateTime, nullable=False)
