"""Repository for Investment entity following segregated interfaces."""
from typing import List

from sqlalchemy import case, func, select

from models import Investment, InvestmentLog
from repositories.core.base_repository import BaseRepository


def _latest_log_column(column):
    """Scalar subquery: the given column of the LATEST non-deleted log of the
    investment being grouped (logs are position snapshots, so the latest row
    holds the current quantity/value for that investment)."""
    return (
        select(column)
        .where(
            InvestmentLog.investment_id == Investment.id,
            InvestmentLog.deleted_at.is_(None),
        )
        .order_by(InvestmentLog.date.desc(), InvestmentLog.id.desc())
        .limit(1)
        .correlate(Investment)
        .scalar_subquery()
    )


class InvestmentRepository(BaseRepository[Investment]):
    """Repository for Investment with custom queries."""

    def __init__(self, db):
        super().__init__(db, Investment)
    def exists_by_dedup(self, account_id: int, dedup_hash: str) -> bool:
        stmt = self._base_query().where(
            Investment.account_id == account_id,
            Investment.dedup_hash == dedup_hash
        )
        return self.db.execute(stmt).scalar_one_or_none() is not None

    def get_totals_without_isin(self) -> tuple[int, float]:
        """(count, sum(amount)) of investments that have no ISIN, for the
        dashboard's 'pending to classify' hint."""
        totals = self.db.execute(
            select(func.count(Investment.id), func.coalesce(func.sum(Investment.amount), 0))
            .where(Investment.deleted_at.is_(None), Investment.isin.is_(None))
        ).one()
        return int(totals[0]), float(totals[1])

    def get_grouped_by_isin(self) -> List[tuple]:
        """One row per ISIN: (isin, total_amount, contributions, last_date).

        Used by the market dashboard; contributions without ISIN are
        excluded (they cannot have market data).
        """
        stmt = (
            select(
                Investment.isin,
                func.sum(Investment.amount).label('total_amount'),
                func.count(Investment.id).label('contributions'),
                func.max(Investment.date).label('last_date'),
            )
            .where(Investment.deleted_at.is_(None), Investment.isin.isnot(None))
            .group_by(Investment.isin)
            .order_by(func.sum(Investment.amount).desc())
        )
        return list(self.db.execute(stmt).all())

    def get_positions_by_isin(self) -> List[tuple]:
        """One row per ISIN with position data from the latest log of each
        investment (logs are snapshots: latest row = current position).

        Returns (isin, contributions, units, investments_with_units,
        reported_value):
        - units: sum of latest-log quantities (0 when nobody logged)
        - investments_with_units: how many of the ISIN's investments have a
          log with quantity, to flag partial coverage
        - reported_value: sum of latest-log current_value (last valuation
          recorded by hand, used as fallback when no market quote exists)
        """
        latest_quantity = _latest_log_column(InvestmentLog.quantity)
        latest_value = _latest_log_column(InvestmentLog.current_value)

        stmt = (
            select(
                Investment.isin,
                func.count(Investment.id).label('contributions'),
                func.coalesce(func.sum(latest_quantity), 0).label('units'),
                func.sum(case((latest_quantity.isnot(None), 1), else_=0))
                    .label('investments_with_units'),
                func.coalesce(func.sum(latest_value), 0).label('reported_value'),
            )
            .where(Investment.deleted_at.is_(None), Investment.isin.isnot(None))
            .group_by(Investment.isin)
        )
        return list(self.db.execute(stmt).all())
