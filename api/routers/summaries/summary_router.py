"""Summary router for aggregation endpoints."""
from datetime import date
from flask import Blueprint, request
from sqlalchemy.orm import Session
from pydantic import ValidationError

from services.summaries.summary_service import SummaryService
from db.database import get_db
from services.core.response_service import Response


router = Blueprint('summaries', __name__)
name = "summaries"


@router.get("/summary")
def get_summary():
    """
    Get summary with aggregations for a date range.
    
    Query Parameters:
    - start_date: YYYY-MM-DD format (required)
    - end_date: YYYY-MM-DD format (required)
    
    Returns:
    {
        "period_start": "2026-01-01",
        "period_end": "2026-03-26",
        "totals_by_category": [
            {
                "category_id": 1,
                "category_name": "Groceries",
                "type": "expense",
                "total": 150.50
            }
        ],
        "totals_over_time": [
            {
                "date": "2026-01-01",
                "expense": 50.0,
                "income": 2000.0,
                "investment": 100.0,
                "net": 1850.0
            }
        ],
        "income_vs_expense": {
            "total_income": 10000.0,
            "total_expense": 5000.0,
            "net": 5000.0,
            "count_transactions": 150
        }
    }
    """
    db: Session = next(get_db())

    try:
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        
        period_type = request.args.get('period', 'custom')  # 'week'|'month'|'year'|'custom'

        # Initialize service
        service = SummaryService(db)

        # Handle predefined periods or custom range
        if period_type == 'week':
            result = service.get_week_summary()
        elif period_type == 'month':
            result = service.get_month_summary()
        elif period_type == 'year':
            result = service.get_year_summary()
        else:  # custom range
            if not start_date_str or not end_date_str:
                return Response.error(
                    "start_date and end_date are required for custom period",
                    400
                )
            
            try:
                start_date = date.fromisoformat(start_date_str)
                end_date = date.fromisoformat(end_date_str)
            except ValueError as e:
                return Response.error(
                    f"Invalid date format. Use YYYY-MM-DD: {str(e)}",
                    400
                )

            result = service.get_summary(start_date, end_date)

        return Response.success(result.model_dump())

    except ValueError as e:
        return Response.error(str(e), 400)
    except Exception as e:
        return Response.error(f"Internal server error: {str(e)}", 500)


@router.get("/summary/week")
def get_week_summary():
    """
    Get summary for current week (Monday-Sunday).
    """
    db: Session = next(get_db())

    try:
        service = SummaryService(db)
        result = service.get_week_summary()
        return Response.success(result.model_dump())
    except Exception as e:
        return Response.error(f"Internal server error: {str(e)}", 500)


@router.get("/summary/month")
def get_month_summary():
    """
    Get summary for current month.
    """
    db: Session = next(get_db())

    try:
        service = SummaryService(db)
        result = service.get_month_summary()
        return Response.success(result.model_dump())
    except Exception as e:
        return Response.error(f"Internal server error: {str(e)}", 500)


@router.get("/summary/year")
def get_year_summary():
    """
    Get summary for current year.
    """
    db: Session = next(get_db())

    try:
        service = SummaryService(db)
        result = service.get_year_summary()
        return Response.success(result.model_dump())
    except Exception as e:
        return Response.error(f"Internal server error: {str(e)}", 500)
