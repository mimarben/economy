"""Summary service for aggregation business logic."""
from datetime import date, timedelta
from sqlalchemy.orm import Session
from repositories.summaries.summary_repository import SummaryRepository
from schemas.summaries.summary_schema import (
    SummaryResponse,
    TotalByCategory,
    TotalOverTime,
    IncomeVsExpense
)


class SummaryService:
    """Service for summary aggregation logic."""

    def __init__(self, db: Session):
        self.db = db
        self.repository = SummaryRepository(db)

    def get_summary(
        self,
        start_date: date,
        end_date: date
    ) -> SummaryResponse:
        """
        Get comprehensive summary for a date range.
        
        Args:
            start_date: Start of period (inclusive)
            end_date: End of period (inclusive)
            
        Returns:
            SummaryResponse with aggregated data
        """
        # Validate dates
        if start_date > end_date:
            raise ValueError("start_date must be <= end_date")

        # Fetch aggregated data
        totals_by_category_raw = self.repository.get_totals_by_category(start_date, end_date)
        totals_over_time_raw = self.repository.get_totals_over_time(start_date, end_date)
        total_income, total_expense, tx_count = self.repository.get_income_vs_expense(
            start_date, end_date
        )

        # Build response objects
        totals_by_category = [
            TotalByCategory(
                category_id=cat_id,
                category_name=cat_name,
                type=tx_type,
                total=total
            )
            for cat_id, cat_name, tx_type, total in totals_by_category_raw
        ]

        totals_over_time = [
            TotalOverTime(
                date=date_key,
                expense=daily['expense'],
                income=daily['income'],
                investment=daily['investment'],
                net=daily['net']
            )
            for date_key, daily in sorted(totals_over_time_raw.items())
        ]

        income_vs_expense = IncomeVsExpense(
            total_income=total_income,
            total_expense=total_expense,
            net=total_income - total_expense,
            count_transactions=tx_count
        )

        return SummaryResponse(
            period_start=start_date,
            period_end=end_date,
            totals_by_category=totals_by_category,
            totals_over_time=totals_over_time,
            income_vs_expense=income_vs_expense
        )

    def get_week_summary(self) -> SummaryResponse:
        """Get summary for current week (Monday-Sunday)."""
        today = date.today()
        start = today - timedelta(days=today.weekday())  # Monday
        end = start + timedelta(days=6)  # Sunday
        return self.get_summary(start, end)

    def get_month_summary(self) -> SummaryResponse:
        """Get summary for current month."""
        today = date.today()
        start = today.replace(day=1)
        
        # Get first day of next month, then subtract 1 day
        if today.month == 12:
            end = date(today.year + 1, 1, 1) - timedelta(days=1)
        else:
            end = date(today.year, today.month + 1, 1) - timedelta(days=1)
        
        return self.get_summary(start, end)

    def get_year_summary(self) -> SummaryResponse:
        """Get summary for current year."""
        today = date.today()
        start = date(today.year, 1, 1)
        end = date(today.year, 12, 31)
        return self.get_summary(start, end)
