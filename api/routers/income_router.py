from flask import Blueprint, request
from sqlalchemy.orm import Session
from pydantic import ValidationError
from flask_babel import _

from schemas.income_schema import IncomeCreate, IncomeUpdate
from services.income_service import IncomeService
from db.database import get_db
from services.response_service import Response


router = Blueprint('incomes', __name__)
name = "incomes"


@router.post("/incomes")
def create_income():
    """
    Create a new income.

    Single Responsibility: Handle HTTP request/response
    Delegates business logic to IncomeService
    """
    db: Session = next(get_db())

    try:
        # ✅ Only validate format, not DB constraints
        income_data = IncomeCreate.model_validate(request.json)
    except ValidationError as e:
        return Response._error(_("VALIDATION_ERROR"), e.errors(), 400, name)

    try:
        # ✅ Delegate to service for business logic & DB validation
        service = IncomeService(db)
        result = service.create_income(income_data)
        return Response._ok_data(
            result.model_dump(),
            _("INCOME_CREATED"),
            201,
            name
        )
    except ValueError as e:
        # ForeignKey validation errors from service
        return Response._error(_("FK_ERROR"), str(e), 400, name)
    except Exception as e:
        return Response._error(_("DATABASE_ERROR"), str(e), 500, name)


@router.get("/incomes/<int:income_id>")
def get_income(income_id):
    """Get a single income by ID."""
    db: Session = next(get_db())

    service = IncomeService(db)
    result = service.get_income(income_id)

    if not result:
        return Response._error(_("INCOME_NOT_FOUND"), _("NONE"), 404, name)

    return Response._ok_data(result.model_dump(), _("INCOME_FOUND"), 200, name)


@router.patch("/incomes/<int:income_id>")
def update_income(income_id):
    """Update an income."""
    db: Session = next(get_db())

    try:
        income_data = IncomeUpdate.model_validate(request.json)
    except ValidationError as e:
        return Response._error(_("VALIDATION_ERROR"), e.errors(), 400, name)

    try:
        service = IncomeService(db)
        result = service.update_income(income_id, income_data)

        if not result:
            return Response._error(_("INCOME_NOT_FOUND"), _("NONE"), 404, name)

        return Response._ok_data(result.model_dump(), _("INCOME_UPDATED"), 200, name)
    except Exception as e:
        return Response._error(_("DATABASE_ERROR"), str(e), 500, name)


@router.delete("/incomes/<int:income_id>")
def delete_income(income_id):
    """Delete an income."""
    db: Session = next(get_db())

    service = IncomeService(db)
    success = service.delete_income(income_id)

    if not success:
        return Response._error(_("INCOME_NOT_FOUND"), _("NONE"), 404, name)

    return Response._error(_("INCOME_DELETED"), _("NONE"), 204, name)


@router.get("/incomes")
def list_incomes():
    """Get all incomes."""
    db: Session = next(get_db())

    service = IncomeService(db)
    results = service.get_all_incomes()

    if not results:
        return Response._error(_("INCOME_NOT_FOUND"), _("NONE"), 404, name)

    return Response._ok_data(
        [r.model_dump() for r in results],
        _("INCOME_FOUND"),
        200,
        name
    )


@router.get("/incomes/user/<int:user_id>")
def get_user_incomes(user_id):
    """Get all incomes for a specific user."""
    db: Session = next(get_db())

    service = IncomeService(db)
    results = service.get_user_incomes(user_id)

    if not results:
        return Response._error(_("INCOME_NOT_FOUND"), _("NONE"), 404, name)

    return Response._ok_data(
        [r.model_dump() for r in results],
        _("INCOME_FOUND"),
        200,
        name
    )
