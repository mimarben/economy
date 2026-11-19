#!/usr/bin/env python3
"""Refresh the market_quotes cache for every ISIN in the portfolio.

Meant to be scheduled (cron, systemd timer, Docker cron...) so the cache is
warm before anyone opens the dashboard and Yahoo's rate limits are only
touched once a night, off-peak:

    # crontab -e  (every day at 06:30, Europe/Madrid)
    30 6 * * * cd /srv/economy/api && uv run python scripts/refresh_market_quotes.py

Runs outside FastAPI on purpose: no server needed, one process, one pass.
"""
import sys
from pathlib import Path

# Allow `uv run python scripts/refresh_market_quotes.py` from api/
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select  # noqa: E402

from db.database import SessionFactory  # noqa: E402
from models import Investment  # noqa: E402
from services.investments.market_quote_service import MarketQuoteService  # noqa: E402
from services.logs.logger_service import setup_logger  # noqa: E402

logger = setup_logger("refresh_market_quotes")


def main() -> int:
    db = SessionFactory()
    try:
        stmt = (
            select(Investment.isin)
            .where(Investment.deleted_at.is_(None), Investment.isin.isnot(None))
            .distinct()
        )
        isins = [row[0] for row in db.execute(stmt).all()]
        if not isins:
            logger.info("No investments with ISIN found; nothing to refresh")
            return 0

        logger.info("Refreshing %d ISINs", len(isins))
        service = MarketQuoteService(db)
        quotes = service.get_quotes(isins, force_refresh=True)

        ok = sum(1 for q in quotes if q.status == "ok")
        stale = sum(1 for q in quotes if q.status == "stale")
        unavailable = sum(1 for q in quotes if q.status == "unavailable")
        logger.info(
            "Done: %d ok, %d stale, %d unavailable (of %d)",
            ok, stale, unavailable, len(quotes),
        )
        for quote in quotes:
            if quote.status != "ok":
                logger.warning("  %s -> %s", quote.isin, quote.status)
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
