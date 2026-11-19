"""Yahoo Finance market data provider.

Resolves an ISIN to a Yahoo symbol via the search endpoint, then reads the
chart endpoint for the current price and previous close. Verified working
for European UCITS funds (quoteType MUTUALFUND, e.g. IE00B83YJG36 ->
0P0000Y354.F), ETFs and stocks.

Uses only the standard library (urllib) on purpose: the API keeps its
dependency footprint minimal and the two GET requests involved are simple.
"""
import json
import logging
import time
from decimal import Decimal
from typing import Any, Optional
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from config import Config

from services.investments.market_provider import MarketDataProvider, ProviderQuote
from services.logs.logger_service import setup_logger

logger = setup_logger("yahoo_market_provider")

_SEARCH_URL = "https://query2.finance.yahoo.com/v1/finance/search"
_CHART_URL = "https://query2.finance.yahoo.com/v8/finance/chart"
_USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/131.0 Safari/537.36"
)
_SUPPORTED_QUOTE_TYPES = {"ETF", "MUTUALFUND", "EQUITY"}
# Yahoo throttles bursts from one IP (HTTP 429): space out requests.
_MIN_REQUEST_INTERVAL_SECONDS = 0.5
# Mirror hosts: on a 429 from one edge, the other sometimes still answers.
_HOST_FALLBACKS = {
    "query1.finance.yahoo.com": "query2.finance.yahoo.com",
    "query2.finance.yahoo.com": "query1.finance.yahoo.com",
}


class YahooMarketProvider(MarketDataProvider):
    """Fetches quotes from Yahoo Finance's public endpoints (no API key)."""

    def __init__(self):
        self._last_request_at = 0.0

    @property
    def source_name(self) -> str:
        return "yahoo"

    def fetch_quote(self, isin: str, known_symbol: Optional[str] = None) -> Optional[ProviderQuote]:
        # Fast path: reuse the symbol cached from a previous fetch so only
        # the chart endpoint is hit (one request instead of two).
        if known_symbol:
            quote = self._build_quote(isin, {"symbol": known_symbol})
            if quote is not None:
                return quote
            logger.info("Cached symbol %s stale for %s, re-resolving", known_symbol, isin)

        symbol_data = self._resolve_symbol(isin)
        if not symbol_data:
            return None
        return self._build_quote(isin, symbol_data)

    # ======================
    # INTERNALS
    # ======================

    def _build_quote(self, isin: str, symbol_data: dict[str, Any]) -> Optional[ProviderQuote]:
        symbol = symbol_data.get("symbol")
        if not symbol:
            return None

        chart_meta = self._fetch_chart_meta(symbol)
        if not chart_meta:
            return None

        last_price = _to_decimal(chart_meta.get("regularMarketPrice"))
        previous_close = _to_decimal(
            chart_meta.get("chartPreviousClose")
            or chart_meta.get("previousClose")
        )
        if last_price is None and previous_close is None:
            return None

        return ProviderQuote(
            isin=isin,
            symbol=symbol,
            name=symbol_data.get("longname") or symbol_data.get("shortname"),
            instrument_type=chart_meta.get("instrumentType") or symbol_data.get("quoteType"),
            currency=chart_meta.get("currency"),
            last_price=last_price,
            previous_close=previous_close,
            source=self.source_name,
        )

    def _resolve_symbol(self, isin: str) -> Optional[dict[str, Any]]:
        """ISIN -> Yahoo symbol through the search endpoint."""
        params = urlencode({"q": isin, "quotesCount": 5})
        payload = self._get_json(f"{_SEARCH_URL}?{params}")
        if not payload:
            return None

        for quote in payload.get("quotes", []):
            if quote.get("quoteType") in _SUPPORTED_QUOTE_TYPES and quote.get("symbol"):
                return quote
        return None

    # ======================
    # INTERNALS
    # ======================

    def _resolve_symbol(self, isin: str) -> Optional[dict[str, Any]]:
        """ISIN -> Yahoo symbol through the search endpoint."""
        params = urlencode({"q": isin, "quotesCount": 5})
        payload = self._get_json(f"{_SEARCH_URL}?{params}")
        if not payload:
            return None

        for quote in payload.get("quotes", []):
            if quote.get("quoteType") in _SUPPORTED_QUOTE_TYPES and quote.get("symbol"):
                return quote
        return None

    def _fetch_chart_meta(self, symbol: str) -> Optional[dict[str, Any]]:
        """Chart endpoint -> meta dict with price/close/currency."""
        params = urlencode({"range": "5d", "interval": "1d"})
        payload = self._get_json(f"{_CHART_URL}/{symbol}?{params}")
        if not payload:
            return None

        results = payload.get("chart", {}).get("result") or []
        if not results:
            return None
        return results[0].get("meta")

    def _get_json(self, url: str) -> Optional[dict[str, Any]]:
        """GET a JSON document; returns None on any transport/parse error.

        On HTTP 429 (edge throttle) retries once against the mirror host.
        """
        timeout = getattr(Config, "MARKET_DATA_TIMEOUT_SECONDS", 10)
        try:
            return self._open_json(url, timeout)
        except HTTPError as error:
            if error.code == 429 and _mirror_url(url) != url:
                mirror = _mirror_url(url)
                logger.info("429 on %s, retrying via %s", url, mirror)
                try:
                    return self._open_json(mirror, timeout)
                except (HTTPError, URLError, TimeoutError, ValueError) as retry_error:
                    logger.warning("Yahoo retry failed for %s: %s", mirror, retry_error)
                    return None
            logger.warning("Yahoo request failed for %s: %s", url, error)
            return None
        except (URLError, TimeoutError, json.JSONDecodeError, ValueError) as error:
            logger.warning("Yahoo request failed for %s: %s", url, error)
            return None

    def _open_json(self, url: str, timeout: float) -> dict[str, Any]:
        """Single throttled GET that raises transport errors to the caller."""
        self._throttle()
        request = Request(url, headers={"User-Agent": _USER_AGENT})
        with urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))

    def _throttle(self) -> None:
        """Sleep just enough to keep requests spaced out (429 protection)."""
        now = time.monotonic()
        wait = self._last_request_at + _MIN_REQUEST_INTERVAL_SECONDS - now
        if wait > 0:
            time.sleep(wait)
        self._last_request_at = time.monotonic()


def _to_decimal(value: Any) -> Optional[Decimal]:
    """Best-effort conversion; Yahoo returns ints/floats or nothing."""
    if value is None:
        return None
    try:
        return Decimal(str(value))
    except (ArithmeticError, ValueError):
        return None


def _mirror_url(url: str) -> str:
    """Swap query1 <-> query2 host, or return the URL unchanged."""
    for host, mirror in _HOST_FALLBACKS.items():
        if host in url:
            return url.replace(host, mirror)
    return url
