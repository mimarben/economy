"""Unit tests for the Yahoo market provider: parsing and resilience.

No network: _get_json / _open_json are replaced with canned payloads.
"""
from decimal import Decimal
from urllib.error import HTTPError

from services.investments.yahoo_market_provider import (
    YahooMarketProvider,
    _mirror_url,
)

ISIN = "IE00B83YJG36"
SYMBOL = "0P0000Y354.F"

_SEARCH_PAYLOAD = {
    "quotes": [
        {"quoteType": "OPTION", "symbol": "IGNORED.X"},
        {
            "quoteType": "MUTUALFUND",
            "symbol": SYMBOL,
            "shortname": SYMBOL,
            "longname": "iShares Developed Real Estate",
        },
    ]
}

_CHART_PAYLOAD = {
    "chart": {
        "result": [{
            "meta": {
                "symbol": SYMBOL,
                "currency": "EUR",
                "instrumentType": "MUTUALFUND",
                "regularMarketPrice": 20.601,
                "chartPreviousClose": 20.547,
            }
        }]
    }
}


def _fake_get_json(responses):
    """Returns a callable serving canned payloads by URL substring."""
    def get_json(url):
        for needle, payload in responses:
            if needle in url:
                return payload
        return None
    return get_json


class TestFetchQuote:
    def test_resolves_isin_and_builds_quote(self):
        provider = YahooMarketProvider()
        provider._get_json = _fake_get_json([
            ("search?", _SEARCH_PAYLOAD),
            ("chart/", _CHART_PAYLOAD),
        ])

        quote = provider.fetch_quote(ISIN)

        assert quote is not None
        assert quote.isin == ISIN
        assert quote.symbol == SYMBOL
        assert quote.name == "iShares Developed Real Estate"
        assert quote.instrument_type == "MUTUALFUND"
        assert quote.currency == "EUR"
        assert quote.last_price == Decimal("20.601")
        assert quote.previous_close == Decimal("20.547")
        assert quote.source == "yahoo"

    def test_known_symbol_skips_search(self):
        provider = YahooMarketProvider()

        def no_search(url):
            assert "search?" not in url, "cached symbol must skip the search endpoint"
            return _CHART_PAYLOAD

        provider._get_json = no_search

        quote = provider.fetch_quote(ISIN, known_symbol=SYMBOL)

        assert quote is not None
        assert quote.symbol == SYMBOL

    def test_known_symbol_re_resolves_when_chart_empty(self):
        provider = YahooMarketProvider()
        empty_chart = {"chart": {"result": []}}
        calls = []

        def get_json(url):
            calls.append("search" if "search?" in url else "chart")
            if "search?" in url:
                return _SEARCH_PAYLOAD
            # First chart call (cached symbol) fails, second (after search) works
            return empty_chart if calls.count("chart") == 1 else _CHART_PAYLOAD

        provider._get_json = get_json

        quote = provider.fetch_quote(ISIN, known_symbol="GONE.F")

        assert quote is not None
        assert quote.symbol == SYMBOL
        assert calls == ["chart", "search", "chart"]

    def test_unsupported_instrument_types_skipped(self):
        provider = YahooMarketProvider()
        provider._get_json = _fake_get_json([
            ("search?", {"quotes": [{"quoteType": "OPTION", "symbol": "X"}]}),
        ])

        assert provider.fetch_quote(ISIN) is None

    def test_no_price_data_returns_none(self):
        provider = YahooMarketProvider()
        empty_meta = {"chart": {"result": [{"meta": {"symbol": SYMBOL}}]}}
        provider._get_json = _fake_get_json([
            ("search?", _SEARCH_PAYLOAD),
            ("chart/", empty_meta),
        ])

        assert provider.fetch_quote(ISIN) is None


class TestRateLimitResilience:
    def test_429_rotates_to_mirror_host(self):
        provider = YahooMarketProvider()
        requested = []

        def open_json(url, timeout):
            requested.append(url)
            if "query2" in url:
                raise HTTPError(url, 429, "Too Many Requests", None, None)
            return _CHART_PAYLOAD

        provider._open_json = open_json

        payload = provider._get_json("https://query2.finance.yahoo.com/v8/finance/chart/X")

        assert payload == _CHART_PAYLOAD
        assert len(requested) == 2
        assert "query1" in requested[1]

    def test_429_on_both_hosts_returns_none(self):
        provider = YahooMarketProvider()

        def open_json(url, timeout):
            raise HTTPError(url, 429, "Too Many Requests", None, None)

        provider._open_json = open_json

        assert provider._get_json("https://query2.finance.yahoo.com/v8/finance/chart/X") is None

    def test_mirror_url_swaps_hosts(self):
        assert "query1" in _mirror_url("https://query2.finance.yahoo.com/x")
        assert "query2" in _mirror_url("https://query1.finance.yahoo.com/x")
        assert _mirror_url("https://example.com/x") == "https://example.com/x"
