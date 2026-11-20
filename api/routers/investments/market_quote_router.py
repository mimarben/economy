"""Router for market quotes and the investments dashboard."""
import re
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from schemas.investments.investment_schema import ISIN_PATTERN
from services.investments.market_quote_service import MarketQuoteService
from services.investments.market_provider import SearchProvider
from services.investments.eulerpool_market_provider import EulerpoolMarketProvider
from db.database import get_db
from services.core.response_service import Response
from utils.i18n import _
from services.auth.auth_dependencies import get_current_user_id

router = APIRouter()
name = "market"

_ISIN_RE = re.compile(ISIN_PATTERN)


def _get_service(db: Session) -> MarketQuoteService:
    """Dependency: service bound to the request session."""
    return MarketQuoteService(db)


def _parse_isins(raw: str) -> List[str]:
    isins = [part.strip().upper() for part in raw.split(",") if part.strip()]
    for isin in isins:
        if len(isin) != 12 or not _ISIN_RE.match(isin):
            raise ValueError(f"INVALID_ISIN: {isin}")
    return isins


@router.get("/market/quotes")
def get_quotes(
    isins: str = Query(..., min_length=12, description="Comma-separated ISINs"),
    refresh: bool = Query(False, description="Bypass the cache TTL"),
    db: Session = Depends(get_db),
):
    try:
        isin_list = _parse_isins(isins)
    except ValueError as e:
        return Response.error(_("VALIDATION_ERROR"), str(e), 400, name)

    try:
        service = _get_service(db)
        results = service.get_quotes(isin_list, force_refresh=refresh)
        return Response.ok_data(
            [r.model_dump() for r in results], _("MARKET_QUOTE_LIST"), 200, name
        )
    except Exception as e:
        return Response.error(_("MARKET_DATA_ERROR"), str(e), 500, name)


@router.get("/investments/dashboard")
def get_dashboard(
    refresh: bool = Query(False, description="Bypass the quote cache TTL"),
    db: Session = Depends(get_db),
    user_id: Optional[int] = Depends(get_current_user_id),
):
    try:
        service = _get_service(db)
        # Admin (role=admin) sees everything, regular users see only their accounts
        result = service.get_dashboard(force_refresh=refresh, user_id=user_id)
        return Response.ok_data(result.model_dump(), _("INVESTMENTS_DASHBOARD"), 200, name)
    except Exception as e:
        return Response.error(_("MARKET_DATA_ERROR"), str(e), 500, name)


@router.get("/market/search")
def search_instruments(
    q: str = Query(..., min_length=1, description="Search query (name, ticker, or ISIN)"),
    limit: int = Query(10, ge=1, le=50, description="Maximum results to return"),
    db: Session = Depends(get_db),
):
    """Search instruments via Eulerpool API (primary) or Yahoo Finance (fallback).

    Returns normalized results without exposing raw JSON to clients.
    """
    try:
        # Use Eulerpool search provider directly (no database dependency)
        provider = EulerpoolMarketProvider()
        results = provider.search_instruments(q, limit=limit)

        from schemas.investments.market_quote_schema import InstrumentSearchResult
        return Response.ok_data(
            [r.model_dump() for r in results], _("MARKET_SEARCH_RESULTS"), 200, name
        )
    except Exception as e:
        return Response.error(_("MARKET_DATA_ERROR"), str(e), 500, name)
