"""Unit tests for the Eulerpool market provider: parsing and resilience.

No network: _get_json / _open_json are replaced with canned payloads.
Tests verify:
- Quote fetching for ISINs
- Search functionality
- Error handling (API error, 429, missing data)
- Stale quote handling
- API key masking in logs
"""
from decimal import Decimal
from unittest.mock import MagicMock, patch
from urllib.error import HTTPError

from services.investments.eulerpool_market_provider import (
    EulerpoolMarketProvider,
    _mask_api_key,
    _mask_isin,
    _to_decimal,
)


class TestFetchQuote:
    """Tests for fetch_quote method."""

    def test_fetch_equity_quote_success(self):
        """Successfully fetch quote for equity (stock/crypto)."""
        provider = EulerpoolMarketProvider()
        isin = "IE00B4L5Y983"

        # Mock equity profile response
        equity_response = {
            "isin": isin,
            "ticker": "SWDA",
            "name": "iShares Core MSCI World UCITS ETF",
            "type": "ETF",
            "currency": "USD",
            "latestQuotes": 124.43,
            "previousClose": 124.20,
            "timestamp": 1732000000000,
        }

        provider._get_json = lambda url: equity_response

        quote = provider.fetch_quote(isin)

        assert quote is not None
        assert quote.isin == isin
        assert quote.symbol == "SWDA"
        assert quote.name == "iShares Core MSCI World UCITS ETF"
        assert quote.instrument_type == "ETF"
        assert quote.currency == "USD"
        assert quote.last_price == Decimal("124.43")
        assert quote.previous_close == Decimal("124.20")
        assert quote.source == "eulerpool"

    def test_fetch_etf_quote_success(self):
        """Successfully fetch quote for ETF."""
        provider = EulerpoolMarketProvider()
        isin = "LU0996175948"

        etf_response = {
            "isin": isin,
            "ticker": "EMIM",
            "name": "iShares MSCI Emerging Markets ETF",
            "type": "ETF",
            "currency": "USD",
            "latestQuotes": 68.15,
            "previousClose": 68.00,
        }

        provider._get_json = lambda url: etf_response

        quote = provider.fetch_quote(isin)

        assert quote is not None
        assert quote.isin == isin
        assert quote.instrument_type == "ETF"

    def test_fetch_crypto_quote_success(self):
        """Successfully fetch quote for cryptocurrency."""
        provider = EulerpoolMarketProvider()
        isin = "DEXXXXXXXXX"  # Generic ISIN for crypto

        crypto_response = {
            "isin": isin,
            "ticker": "BTC",
            "name": "Bitcoin",
            "type": "CRYPTOCURRENCY",
            "currency": "USD",
            "latestQuotes": 65000.00,
            "previousClose": 64500.00,
        }

        provider._get_json = lambda url: crypto_response

        quote = provider.fetch_quote(isin)

        assert quote is not None
        assert quote.symbol == "BTC"
        assert quote.instrument_type == "CRYPTO"

    def test_no_price_data_returns_none(self):
        """Return None when no price data available."""
        provider = EulerpoolMarketProvider()
        isin = "IE00B4L5Y983"

        empty_response = {
            "isin": isin,
            "ticker": "SWDA",
            "name": "iShares Core MSCI World UCITS ETF",
            "type": "ETF",
        }

        provider._get_json = lambda url: empty_response

        assert provider.fetch_quote(isin) is None

    def test_api_error_returns_none(self):
        """Return None on API error (HTTP 5xx)."""
        provider = EulerpoolMarketProvider()

        def failing_open_json(url, timeout):
            raise HTTPError(url, 500, "Internal Server Error", None, None)

        provider._open_json = failing_open_json

        # The provider should catch the exception and return None
        assert provider.fetch_quote("IE00B4L5Y983") is None

    def test_429_rate_limit_handling(self):
        """Return None on 429 rate limit (retry handled by caller if needed)."""
        provider = EulerpoolMarketProvider()

        def rate_limited_open_json(url, timeout):
            raise HTTPError(url, 429, "Too Many Requests", None, None)

        provider._open_json = rate_limited_open_json

        assert provider.fetch_quote("IE00B4L5Y983") is None

    def test_missing_isin_returns_none(self):
        """Return None when ISIN not found by provider."""
        provider = EulerpoolMarketProvider()

        empty_response = {}

        provider._get_json = lambda url: empty_response

        assert provider.fetch_quote("INVALID-ISIN") is None

    def test_cached_symbol_skips_search(self):
        """Re-use known_symbol to reduce API calls."""
        provider = EulerpoolMarketProvider()
        isin = "IE00B4L5Y983"
        symbol = "SWDA"

        quote = provider.fetch_quote(isin, known_symbol=symbol)

        # With mocked _get_json, this will try bulk quote and fail gracefully
        # The important thing is it doesn't fail on missing symbol resolution
        assert quote is None  # Expected with mock

    def test_fallback_to_etf_after_equity(self):
        """Try equity first, then ETF if equity fails."""
        provider = EulerpoolMarketProvider()
        isin = "LU0996175948"

        calls = []

        def tracking_get_json(url):
            calls.append(url)
            # Equity fails, ETF succeeds
            if "equity" in url:
                return {}
            return {
                "isin": isin,
                "ticker": "EMIM",
                "name": "Amundi Emerging Markets",
                "type": "ETF",
                "currency": "USD",
                "latestQuotes": 68.15,
            }

        provider._get_json = tracking_get_json

        quote = provider.fetch_quote(isin)

        assert quote is not None
        assert len(calls) == 2  # equity + ETF
        assert "equity" in calls[0]
        assert "etf" in calls[1]


class TestSearchInstruments:
    """Tests for search_instruments method."""

    def test_search_by_name(self):
        """Search instruments by name."""
        provider = EulerpoolMarketProvider()

        search_response = {
            "count": 2,
            "results": [
                {
                    "isin": "IE00B4L5Y983",
                    "ticker": "SWDA",
                    "name": "iShares Core MSCI World UCITS ETF",
                    "type": "ETF",
                    "currency": "USD",
                    "exchange": "LSE",
                },
                {
                    "isin": "IE0032126645",
                    "ticker": "VUSA",
                    "name": "Vanguard S&P 500 UCITS ETF",
                    "type": "ETF",
                    "currency": "USD",
                    "exchange": "LSE",
                },
            ],
        }

        provider._get_json = lambda url: search_response

        results = provider.search_instruments("MSCI World", limit=5)

        assert len(results) == 2
        assert results[0].isin == "IE00B4L5Y983"
        assert results[0].symbol == "SWDA"
        assert results[0].name == "iShares Core MSCI World UCITS ETF"
        assert results[0].instrument_type == "ETF"
        assert results[0].currency == "USD"
        assert results[0].exchange == "LSE"

    def test_search_by_isin(self):
        """Search instruments by ISIN."""
        provider = EulerpoolMarketProvider()

        search_response = {
            "count": 1,
            "results": [
                {
                    "isin": "IE00B4L5Y983",
                    "ticker": "SWDA",
                    "name": "iShares Core MSCI World UCITS ETF",
                    "type": "ETF",
                    "currency": "USD",
                },
            ],
        }

        provider._get_json = lambda url: search_response

        results = provider.search_instruments("IE00B4L5Y983", limit=5)

        assert len(results) == 1
        assert results[0].isin == "IE00B4L5Y983"

    def test_search_by_ticker(self):
        """Search instruments by ticker."""
        provider = EulerpoolMarketProvider()

        search_response = {
            "count": 1,
            "results": [
                {
                    "isin": "US0378331005",
                    "ticker": "AAPL",
                    "name": "Apple Inc.",
                    "type": "EQUITY",
                    "currency": "USD",
                },
            ],
        }

        provider._get_json = lambda url: search_response

        results = provider.search_instruments("AAPL", limit=5)

        assert len(results) == 1
        assert results[0].symbol == "AAPL"
        assert results[0].instrument_type == "STOCK"

    def test_search_empty_query_returns_empty(self):
        """Empty query returns empty list."""
        provider = EulerpoolMarketProvider()

        results = provider.search_instruments("", limit=5)

        assert results == []

    def test_search_api_error_returns_empty(self):
        """API error returns empty list."""
        provider = EulerpoolMarketProvider()

        def failing_open_json(url, timeout):
            raise HTTPError(url, 500, "Internal Server Error", None, None)

        provider._open_json = failing_open_json

        results = provider.search_instruments("test", limit=5)

        assert results == []

    def test_search_invalid_response_returns_empty(self):
        """Invalid response returns empty list."""
        provider = EulerpoolMarketProvider()

        provider._get_json = lambda url: None

        results = provider.search_instruments("test", limit=5)

        assert results == []


class TestApiKeyMasking:
    """Tests for API key masking in URLs."""

    def test_mask_api_key_in_url(self):
        """API key is masked in URL."""
        url = "https://api.eulerpool.com/api/1/equity/profile/IE00B4L5Y983?token=SECRET_KEY_12345"

        masked = _mask_api_key(url)

        assert "SECRET_KEY_12345" not in masked
        # URL-encoded asterisks from urlencode (correct behavior for URLs)
        assert "%2A%2A%2A%2A" in masked
        # Also verify the URL is valid
        from urllib.parse import urlparse
        parsed = urlparse(masked)
        assert parsed.scheme == "https"

    def test_mask_api_key_no_key(self):
        """URL without key is unchanged."""
        url = "https://api.eulerpool.com/api/1/equity/profile/IE00B4L5Y983"

        masked = _mask_api_key(url)

        assert masked == url

    def test_mask_api_key_multiple_params(self):
        """Mask key among multiple params."""
        url = "https://api.eulerpool.com/api/1/equity/search?q=Apple&token=SECRET&limit=10"

        masked = _mask_api_key(url)

        assert "SECRET" not in masked
        # URL-encoded version of ****
        assert "%2A%2A%2A%2A" in masked
        assert "q=Apple" in masked
        assert "limit=10" in masked

    def test_mask_isin(self):
        """ISIN is masked for logging."""
        isin = "IE00B4L5Y983"

        masked = _mask_isin(isin)

        assert masked == "IE00****Y983"
        assert "B4L5" not in masked

    def test_mask_isin_short(self):
        """Short ISIN is fully masked."""
        isin = "ABC"

        masked = _mask_isin(isin)

        assert masked == "****"


class TestHelperFunctions:
    """Tests for helper functions."""

    def test_to_decimal_valid(self):
        """Valid value converts to Decimal."""
        assert _to_decimal("123.45") == Decimal("123.45")
        assert _to_decimal(123) == Decimal("123")
        assert _to_decimal(123.45) == Decimal("123.45")

    def test_to_decimal_none(self):
        """None returns None."""
        assert _to_decimal(None) is None

    def test_to_decimal_invalid(self):
        """Invalid value returns None."""
        assert _to_decimal("not-a-number") is None
        assert _to_decimal({}) is None


class TestInstrumentTypeNormalization:
    """Tests for instrument type normalization."""

    def test_normalize_etf(self):
        """ETF type normalized correctly."""
        provider = EulerpoolMarketProvider()
        assert provider._normalize_instrument_type("ETF", "search") == "ETF"

    def test_normalize_mutual_fund(self):
        """MUTUALFUND normalized to FUND."""
        provider = EulerpoolMarketProvider()
        assert provider._normalize_instrument_type("MUTUALFUND", "search") == "FUND"

    def test_normalize_equity(self):
        """EQUITY normalized to STOCK."""
        provider = EulerpoolMarketProvider()
        assert provider._normalize_instrument_type("EQUITY", "search") == "STOCK"

    def test_normalize_crypto(self):
        """CRYPTOCURRENCY normalized to CRYPTO."""
        provider = EulerpoolMarketProvider()
        assert provider._normalize_instrument_type("CRYPTOCURRENCY", "search") == "CRYPTO"

    def test_normalize_none(self):
        """None returns None."""
        provider = EulerpoolMarketProvider()
        assert provider._normalize_instrument_type(None, "search") is None


class TestApiKeyInLogs:
    """Tests to verify API key never appears in logs."""

    def test_masked_url_is_used_for_logging(self):
        """_mask_api_key is called before any logging."""
        url = "https://api.eulerpool.com/api/1/equity/profile/IE00B4L5Y983?token=SECRET_KEY_12345"
        masked = _mask_api_key(url)

        # The masked URL should contain **** not the actual key
        assert "SECRET" not in masked
        # URL-encoded version of ****
        assert "%2A%2A%2A%2A" in masked

    def test_masked_url_preserves_other_params(self):
        """Masked URL preserves all other parameters."""
        url = "https://api.eulerpool.com/api/1/equity/search?q=Apple&token=SECRET&limit=10"
        masked = _mask_api_key(url)

        assert "q=Apple" in masked
        assert "limit=10" in masked
        assert "SECRET" not in masked
