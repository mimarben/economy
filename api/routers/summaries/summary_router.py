"""Summary router for aggregation endpoints."""
from fastapi import APIRouter, Body, Depends, Query, Request
from typing import Any
from datetime import date
from sqlalchemy.orm import Session
from pydantic import ValidationError

from services.summaries.summary_service import SummaryService
from db.database import get_db
from services.core.response_service import Response


router = APIRouter()
name = "summaries"


@router.get("/summary")
def get_summary(start_date_str: str | None = Query(default=None, alias="start_date"), end_date_str: str | None = Query(default=None, alias="end_date"), period_type: str = Query(default="custom", alias="period"), db: Session = Depends(get_db)):
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
    try:
        # Initialize service
        service = SummaryService(db)

        # Handle predefined periods or custom range
        if period_type == 'today':
            result = service.get_today_summary()
        elif period_type == 'week':
            result = service.get_week_summary()
        elif period_type == 'month':
            result = service.get_month_summary()
        elif period_type == 'year':
            result = service.get_year_summary()
        else:  # custom range
            if not start_date_str or not end_date_str:
                return Response.error(
                    "VALIDATION_ERROR",
                    "SUMMARY_DATES_REQUIRED",
                    400,
                    name
                )
            
            try:
                start_date = date.fromisoformat(start_date_str)
                end_date = date.fromisoformat(end_date_str)
            except ValueError:
                return Response.error(
                    "VALIDATION_ERROR",
                    "SUMMARY_DATE_INVALID",
                    400,
                    name
                )

            result = service.get_summary(start_date, end_date)

        return Response.ok_data(result.model_dump(), "SUMMARY_FOUND", 200, name)

    except ValueError:
        return Response.error("VALIDATION_ERROR", "SUMMARY_DATE_INVALID", 400, name)
    except Exception:
        return Response.error("DATABASE_ERROR", "UNEXPECTED_ERROR", 500, name)


@router.get("/summary/today")
def get_today_summary(db: Session = Depends(get_db)):
    """Get summary for today."""
    try:
        service = SummaryService(db)
        result = service.get_today_summary()
        return Response.ok_data(result.model_dump(), "SUMMARY_FOUND", 200, name)
    except Exception:
        return Response.error("DATABASE_ERROR", "UNEXPECTED_ERROR", 500, name)


@router.get("/summary/week")
def get_week_summary(db: Session = Depends(get_db)):
    """
    Get summary for current week (Monday-Sunday).
    """
    try:
        service = SummaryService(db)
        result = service.get_week_summary()
        return Response.ok_data(result.model_dump(), "SUMMARY_FOUND", 200, name)
    except Exception:
        return Response.error("DATABASE_ERROR", "UNEXPECTED_ERROR", 500, name)


@router.get("/summary/month")
def get_month_summary(db: Session = Depends(get_db)):
    """
    Get summary for current month.
    """
    try:
        service = SummaryService(db)
        result = service.get_month_summary()
        return Response.ok_data(result.model_dump(), "SUMMARY_FOUND", 200, name)
    except Exception:
        return Response.error("DATABASE_ERROR", "UNEXPECTED_ERROR", 500, name)


@router.get("/summary/year")
def get_year_summary(db: Session = Depends(get_db)):
    """
    Get summary for current year.
    """
    try:
        service = SummaryService(db)
        result = service.get_year_summary()
        return Response.ok_data(result.model_dump(), "SUMMARY_FOUND", 200, name)
    except Exception:
        return Response.error("DATABASE_ERROR", "UNEXPECTED_ERROR", 500, name)
