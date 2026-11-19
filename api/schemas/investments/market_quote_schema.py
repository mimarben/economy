"""Schemas for market quotes (fund/ETF/stock prices) and the investments dashboard."""
from datetime import date as DateType, datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field

from schemas.core.audit_schema import AuditFields


class MarketQuoteBase(BaseModel):
    """Base schema for MarketQuote aligned with ORM model."""

    isin: str = Field(..., min_length=12, max_length=12)
    symbol: Optional[str] = Field(None, max_length=32)
    name: Optional[str] = Field(None, max_length=255)
    instrument_type: Optional[str] = Field(None, max_length=32)
    currency: Optional[str] = Field(None, max_length=8)
    last_price: Optional[Decimal] = Field(None)
    previous_close: Optional[Decimal] = Field(None)
    source: Optional[str] = Field(None, max_length=20)
    fetched_at: datetime = Field(...)


class MarketQuoteRead(MarketQuoteBase, AuditFields):
    """Response schema for MarketQuote."""

    id: int

    class Config:
        from_attributes = True


class MarketQuoteOut(BaseModel):
    """Quote as served to clients: cached data plus computed day change."""

    isin: str
    symbol: Optional[str] = None
    name: Optional[str] = None
    instrument_type: Optional[str] = None
    currency: Optional[str] = None
    last_price: Optional[Decimal] = None
    previous_close: Optional[Decimal] = None
    change_abs: Optional[Decimal] = None
    change_pct: Optional[Decimal] = None
    source: Optional[str] = None
    fetched_at: Optional[datetime] = None
    status: str = Field("ok", description="ok | stale | unavailable")


class DashboardEntry(BaseModel):
    """One ISIN in the user's portfolio: contributions joined with its quote."""

    isin: str
    name: Optional[str] = None
    symbol: Optional[str] = None
    instrument_type: Optional[str] = None
    currency: Optional[str] = None
    total_contributed: Decimal
    contributions: int
    last_contribution_date: Optional[DateType] = None
    # Position (from the latest investment log of each contribution)
    units: Optional[Decimal] = Field(None, description="Units held, None when never logged")
    units_partial: bool = Field(False, description="True when some contributions have no log")
    reported_value: Optional[Decimal] = Field(None, description="Last hand-recorded valuation")
    # Market data
    last_price: Optional[Decimal] = None
    previous_close: Optional[Decimal] = None
    change_abs: Optional[Decimal] = None
    change_pct: Optional[Decimal] = None
    # Valuation
    market_value: Optional[Decimal] = Field(None, description="units x last_price")
    unrealized_pl: Optional[Decimal] = Field(None, description="market_value - total_contributed")
    unrealized_pl_pct: Optional[Decimal] = None
    source: Optional[str] = None
    fetched_at: Optional[datetime] = None
    quote_status: str = "ok"


class DashboardResponse(BaseModel):
    """Aggregated portfolio view grouped by ISIN."""

    entries: List[DashboardEntry] = []
    without_isin_count: int = 0
    without_isin_amount: Decimal = Field(default=Decimal("0"))
    total_contributed: Decimal = Field(default=Decimal("0"))
    total_market_value: Optional[Decimal] = Field(
        None, description="Sum of market_value of entries that have one"
    )
    total_unrealized_pl: Optional[Decimal] = Field(
        None, description="Sum of unrealized_pl of entries that have one"
    )
    generated_at: datetime
