import enum

from sqlalchemy import Column, Integer, String, Numeric, Enum as SQLEnum, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from ..core.base import Base, TimestampMixin
from ..core.enums import CurrencyEnum


class AssetClassEnum(str, enum.Enum):
    ETF = "ETF"
    FUND = "FUND"
    STOCK = "STOCK"
    CRYPTO = "CRYPTO"
    BOND = "BOND"
    MANAGED_PORTFOLIO = "MANAGED_PORTFOLIO"
    OTHER = "OTHER"


class Instrument(TimestampMixin, Base):
    __tablename__ = 'instruments'

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(String, nullable=True)
    asset_class = Column(SQLEnum(AssetClassEnum), nullable=False)
    category_id = Column(Integer, ForeignKey('investments_categories.id'), nullable=False)
    instrument_type = Column(String(32), nullable=True)
    currency = Column(SQLEnum(CurrencyEnum), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    category = relationship('InvestmentsCategory', back_populates='instruments')
    identifiers = relationship('InstrumentIdentifier', back_populates='instrument', cascade='all, delete-orphan')
    compositions_parent = relationship('InstrumentComposition', foreign_keys='InstrumentComposition.parent_instrument_id', back_populates='parent_instrument', cascade='all, delete-orphan')
    compositions_child = relationship('InstrumentComposition', foreign_keys='InstrumentComposition.child_instrument_id', back_populates='child_instrument', cascade='all, delete-orphan')
    investments = relationship('Investment', back_populates='instrument')
    market_quotes = relationship('MarketQuote', back_populates='instrument')
    market_quote_history = relationship('MarketQuoteHistory', back_populates='instrument')
