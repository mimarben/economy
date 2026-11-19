"""Wiring tests for the market quotes router (no HTTP client needed).

Mirrors test_user_roles_router.py: walk the FastAPI route objects and the
router registration to prove the endpoints exist, validate ISINs and are
registered behind the auth dependency.
"""
import pytest
from fastapi import FastAPI

import routers
from routers.investments.market_quote_router import _parse_isins, router as market_quote_router


def _route(path: str, method: str):
    for route in market_quote_router.routes:
        if route.path == path and route.methods and method in route.methods:
            return route
    raise AssertionError(f"Route {method} {path} not found on the market router")


class TestRoutes:
    def test_quotes_route_exists(self):
        route = _route("/market/quotes", "GET")
        query_names = {param.name for param in route.dependant.query_params}
        assert {"isins", "refresh"} <= query_names

    def test_dashboard_route_exists(self):
        _route("/investments/dashboard", "GET")

    def test_router_registered_as_protected(self):
        """The market router must sit behind require_access_token like the rest."""
        assert market_quote_router in routers._protected_routers

    def test_dashboard_path_does_not_collide_with_investment_detail(self):
        """'/investments/{id:int}' must not swallow '/investments/dashboard'."""
        from routers.investments.investment_router import router as investment_router

        for route in investment_router.routes:
            if route.path == "/investments/{id:int}":
                break
        else:
            pytest.fail("investment detail route not found")


class TestParseIsins:
    def test_single_isin(self):
        assert _parse_isins("IE00B83YJG36") == ["IE00B83YJG36"]

    def test_multiple_isins_normalized(self):
        result = _parse_isins(" ie00b83yjg36 , LU0996175948")
        assert result == ["IE00B83YJG36", "LU0996175948"]

    def test_empty_parts_dropped(self):
        assert _parse_isins("IE00B83YJG36,,, ,") == ["IE00B83YJG36"]

    def test_invalid_isin_rejected(self):
        with pytest.raises(ValueError) as exc:
            _parse_isins("IE00B83YJG36,12NOTANISIN1")
        assert "INVALID_ISIN" in str(exc.value)
