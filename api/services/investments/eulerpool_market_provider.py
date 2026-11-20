"""Eulerpool market data provider.

Fetches quotes and performs instrument search via the Eulerpool API.
Uses only standard library (urllib) to keep dependencies minimal.
"""
import json
import logging
import time
from decimal import Decimal
from typing import Any, Optional
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlparse, parse_qs
from urllib.request import Request, urlopen

from config import Config

from services.investments.market_provider import (
    MarketDataProvider,
    ProviderQuote,
    SearchProvider,
    InstrumentSearchResult,
)
from services.logs.logger_service import setup_logger

logger = setup_logger("eulerpool_market_provider")

# Base URL and endpoints
_BASE_URL = "https://api.eulerpool.com"
_API_VERSION = "1"
_EQUITY_PROFILE_ENDPOINT = "/api/{version}/equity/profile"
_EQUITY_SEARCH_ENDPOINT = "/api/{version}/equity/search"
_ETF_PROFILE_ENDPOINT = "/api/{version}/etf/profile"
_MARKET_QUOTES_LATEST_ENDPOINT = "/api/{version}/market/quotes/latest"

# Eulerpool allows both API key as query param or Bearer token
# We use query param to avoid logging the key in headers
_API_KEY_PARAM = "token"


class EulerpoolMarketProvider(MarketDataProvider, SearchProvider):
    """Fetches quotes and performs search via Eulerpool API.

    Primary provider with Yahoo Finance as fallback.
    Uses API key stored in config, never logged or printed.
    """

    def __init__(self):
        self._api_url = Config.EULERPOOL_API_URL.rstrip("/")
        self._api_key = Config.EULERPOOL_API_KEY
        self._last_request_at = 0.0
        # Throttle: Eulerpool free tier allows ~3.8 req/s (100k/month)
        # Use 0.3s minimum to stay well under limits
        self._min_request_interval_seconds = 0.3

    @property
    def source_name(self) -> str:
        return "eulerpool"

    # ======================
    # MarketDataProvider
    # ======================

    def fetch_quote(self, isin: str, known_symbol: Optional[str] = None) -> Optional[ProviderQuote]:
        """Fetch quote for ISIN using Eulerpool API.

        Tries equity profile first (covers stocks, crypto), then ETF profile.
        Returns None if not found or on error.
        """
        # Fast path: if we have a symbol from a previous fetch, try bulk quotes
        if known_symbol:
            quote = self._try_bulk_quote(isin, known_symbol)
            if quote is not None:
                return quote
            logger.info("Cached symbol %s stale for %s, re-resolving", known_symbol, isin)

        # Try equity endpoint (covers stocks, crypto, and some funds)
        quote = self._fetch_equity_quote(isin)
        if quote is not None:
            return quote

        # Try ETF endpoint (for UCITS funds)
        quote = self._fetch_etf_quote(isin)
        if quote is not None:
            return quote

        logger.warning("Eulerpool could not resolve ISIN %s", _mask_isin(isin))
        return None

    # ======================
    # SearchProvider
    # ======================

    def search_instruments(self, query: str, limit: int = 10) -> list[InstrumentSearchResult]:
        """Search instruments by name, ticker, or ISIN.

        Uses equity/search endpoint which covers stocks, ETFs, crypto, bonds, funds.
        Returns normalized results without exposing raw JSON to models.
        """
        if not query or not query.strip():
            return []

        url = self._build_url(_EQUITY_SEARCH_ENDPOINT, {"q": query[:100], "limit": str(limit)})
        payload = self._get_json(url)

        if not payload or not isinstance(payload, dict):
            return []

        results = payload.get("results", [])
        if not results:
            return []

        return [self._normalize_search_result(item) for item in results if self._is_valid_search_result(item)]

    # ======================
    # INTERNALS
    # ======================

    def _fetch_equity_quote(self, isin: str) -> Optional[ProviderQuote]:
        """Fetch quote via equity/profile endpoint (covers stocks, crypto, some funds)."""
        url = self._build_url(_EQUITY_PROFILE_ENDPOINT, {"identifier": isin})
        payload = self._get_json(url)

        if not payload or not isinstance(payload, dict):
            return None

        return self._build_quote_from_profile(isin, payload, "equity")

    def _fetch_etf_quote(self, isin: str) -> Optional[ProviderQuote]:
        """Fetch quote via etf/profile endpoint (UCITS funds)."""
        url = self._build_url(_ETF_PROFILE_ENDPOINT, {"identifier": isin})
        payload = self._get_json(url)

        if not payload or not isinstance(payload, dict):
            return None

        return self._build_quote_from_profile(isin, payload, "etf")

    def _try_bulk_quote(self, isin: str, symbol: str) -> Optional[ProviderQuote]:
        """Try bulk quotes endpoint with known symbol (faster for dashboard refresh)."""
        url = self._build_url(_MARKET_QUOTES_LATEST_ENDPOINT, {"symbols": symbol})
        payload = self._get_json(url)

        if not payload or not isinstance(payload, dict):
            return None

        quotes = payload.get("quotes", [])
        if not quotes:
            return None

        # Bulk endpoint returns symbol, need to map back to ISIN
        for q in quotes:
            if q.get("symbol") == symbol:
                return ProviderQuote(
                    isin=isin,
                    symbol=symbol,
                    name=q.get("name"),
                    instrument_type=q.get("type"),
                    currency=q.get("currency"),
                    last_price=_to_decimal(q.get("price")),
                    previous_close=_to_decimal(q.get("previousClose")),
                    source=self.source_name,
                )
        return None

    def _build_quote_from_profile(
        self, isin: str, profile: dict[str, Any], provider_type: str
    ) -> Optional[ProviderQuote]:
        """Build ProviderQuote from equity/etf profile response."""
        last_price = _to_decimal(profile.get("latestQuotes") or profile.get("price"))
        previous_close = _to_decimal(profile.get("previousClose"))

        if last_price is None and previous_close is None:
            return None

        # Get the timestamp of the quote for quoted_at
        quoted_at = None
        if profile.get("timestamp"):
            try:
                # Eulerpool returns Unix timestamp in milliseconds
                ts = int(profile["timestamp"])
                from datetime import datetime
                quoted_at = datetime.utcfromtimestamp(ts / 1000)
            except (ValueError, TypeError, OSError):
                pass

        return ProviderQuote(
            isin=isin,
            symbol=profile.get("ticker") or profile.get("symbol"),
            name=profile.get("name"),
            instrument_type=self._normalize_instrument_type(profile.get("type") or profile.get("quoteType"), provider_type),
            currency=profile.get("currency"),
            last_price=last_price,
            previous_close=previous_close,
            source=self.source_name,
        )

    def _normalize_instrument_type(self, raw_type: Optional[str], provider_type: str) -> Optional[str]:
        """Normalize instrument type from Eulerpool to standard values."""
        if not raw_type:
            return None

        raw = raw_type.upper()
        type_map = {
            "EQUITY": "STOCK",
            "ETF": "ETF",
            "MUTUALFUND": "FUND",
            "CRYPTOCURRENCY": "CRYPTO",
            "BOND": "BOND",
            "INDEX": "OTHER",
        }
        return type_map.get(raw, raw)

    def _normalize_search_result(self, item: dict[str, Any]) -> InstrumentSearchResult:
        """Normalize raw Eulerpool search result to InstrumentSearchResult."""
        return InstrumentSearchResult(
            isin=item.get("isin", ""),
            symbol=item.get("ticker") or item.get("symbol"),
            name=item.get("name"),
            instrument_type=self._normalize_instrument_type(item.get("type"), "search"),
            currency=item.get("currency"),
            exchange=item.get("exchange") or item.get("exchangeName"),
            country=item.get("country"),
            provider="eulerpool",
        )

    def _is_valid_search_result(self, item: dict[str, Any]) -> bool:
        """Check if search result has minimum required data."""
        return bool(item.get("isin") or item.get("ticker") or item.get("symbol"))

    def _build_url(self, endpoint_template: str, params: dict[str, Any]) -> str:
        """Build full URL with API key and additional params."""
        endpoint = endpoint_template.format(version=_API_VERSION)
        all_params = {**params, _API_KEY_PARAM: self._api_key}
        query = urlencode(all_params)
        return f"{self._api_url}{endpoint}?{query}"

    def _get_json(self, url: str) -> Optional[dict[str, Any]]:
        """GET a JSON document; returns None on any transport/parse error.

        Logs the URL without the API key.
        """
        timeout = getattr(Config, "MARKET_DATA_TIMEOUT_SECONDS", 10)
        masked_url = _mask_api_key(url)

        try:
            return self._open_json(url, timeout)
        except HTTPError as error:
            logger.warning("Eulerpool HTTP error for %s: status=%d", masked_url, error.code)
            return None
        except (URLError, TimeoutError, json.JSONDecodeError, ValueError) as error:
            logger.warning("Eulerpool request failed for %s: %s", masked_url, error)
            return None

    def _open_json(self, url: str, timeout: float) -> dict[str, Any]:
        """Single throttled GET that raises transport errors to the caller."""
        self._throttle()
        request = Request(url, headers={"User-Agent": "EconomyApp/1.0"})
        with urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))

    def _throttle(self) -> None:
        """Sleep to keep requests spaced out (rate limit protection)."""
        now = time.monotonic()
        wait = self._last_request_at + self._min_request_interval_seconds - now
        if wait > 0:
            time.sleep(wait)
        self._last_request_at = time.monotonic()


def _to_decimal(value: Any) -> Optional[Decimal]:
    """Best-effort conversion; Eulerpool returns ints/floats or nothing."""
    if value is None:
        return None
    try:
        return Decimal(str(value))
    except (ArithmeticError, ValueError):
        return None


def _mask_isin(isin: str) -> str:
    """Mask ISIN for logging (show first 4 and last 4 chars)."""
    if not isin or len(isin) < 8:
        return "****"
    return f"{isin[:4]}****{isin[-4:]}"


def _mask_api_key(url: str) -> str:
    """Remove API key from URL for safe logging.

    Handles both ?token=KEY and ?KEY as query param formats.
    """
    if not url:
        return url

    parsed = urlparse(url)
    if not parsed.query:
        return url

    # Parse query params
    params = parse_qs(parsed.query)

    # Remove key-like parameters
    key_params = ["token", "api_key", "apikey", "key", "auth", "auth_token"]
    for param in key_params:
        if param in params:
            params[param] = ["****"]

    # Rebuild query string
    new_query = urlencode(params, doseq=True)
    new_url = parsed._replace(query=new_query).geturl()

    return new_url
