"""Market data provider contract.

Providers fetch quotes (last price, previous close, ...) for an ISIN from an
external service. They are tried in order by MarketQuoteService until one
returns a quote, so a second free API can be added later by implementing
this interface and appending it to the providers list in the service.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional


@dataclass(frozen=True)
class ProviderQuote:
    """Quote returned by a provider for one ISIN."""

    isin: str
    symbol: Optional[str]
    name: Optional[str]
    instrument_type: Optional[str]
    currency: Optional[str]
    last_price: Optional[Decimal]
    previous_close: Optional[Decimal]
    source: str


class MarketDataProvider(ABC):
    """Interface for market data sources (Yahoo Finance, Stooq, ...)."""

    @property
    @abstractmethod
    def source_name(self) -> str:
        """Short identifier stored in market_quotes.source."""

    @abstractmethod
    def fetch_quote(self, isin: str, known_symbol: Optional[str] = None) -> Optional[ProviderQuote]:
        """Fetch the current quote for an ISIN.

        `known_symbol` is the provider symbol cached from a previous
        fetch: providers should use it to skip their ISIN->symbol
        resolution step when possible (fewer requests, less throttling).

        Returns None when the provider cannot resolve the ISIN or the
        request fails — never raises, so one bad ISIN does not break the
        whole dashboard refresh.
        """
