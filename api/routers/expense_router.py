from flask import Blueprint, request
from sqlalchemy.orm import Session
from pydantic import ValidationError
from flask_babel import _

from schemas.expense_schema import ExpenseCreate, ExpenseUpdate
from services.expense_service import ExpenseService
from services.interfaces import ICreateService, IReadService, IUpdateService, IDeleteService
from db.database import get_db
from services.response_service import Response


router = Blueprint('expenses', __name__)
name = "expenses"


def _get_create_service(db: Session) -> ICreateService:
    """Dependency: Inject only create service for POST endpoints."""
    return ExpenseService(db)


def _get_read_service(db: Session) -> IReadService:
    """Dependency: Inject only read service for GET endpoints."""
    return ExpenseService(db)


def _get_update_service(db: Session) -> IUpdateService:
    """Dependency: Inject only update service for PATCH endpoints."""
    return ExpenseService(db)


def _get_delete_service(db: Session) -> IDeleteService:
    """Dependency: Inject only delete service for DELETE endpoints."""
    return ExpenseService(db)


@router.post("/expenses")
def create_expense():
    """
    Create a new expense.

    Single Responsibility: Handle HTTP request/response
    Depends only on ICreateService interface (ISP)
    """
    db: Session = next(get_db())

    try:
        # ✅ Only validate format, not DB constraints
        expense_data = ExpenseCreate.model_validate(request.json)
    except ValidationError as e:
        return Response._error(_("VALIDATION_ERROR"), e.errors(), 400, name)

    try:
        # ✅ Depend only on create interface
        service: ICreateService = _get_create_service(db)
        result = service.create(expense_data)
        return Response._ok_data(
            result.model_dump(),
            _("EXPENSE_CREATED"),
            201,
            name
        )
    except ValueError as e:
        # ForeignKey validation errors from service
        return Response._error(_("FK_ERROR"), str(e), 400, name)
    except Exception as e:
        return Response._error(_("DATABASE_ERROR"), str(e), 500, name)


@router.get("/expenses/<int:expense_id>")
def get_expense(expense_id):
    """Get a single expense by ID."""
    db: Session = next(get_db())

    # Depend only on read interface
    service: IReadService = _get_read_service(db)
    result = service.get_by_id(expense_id)

    if not result:
        return Response._error(_("EXPENSE_NOT_FOUND"), _("NONE"), 404, name)

    return Response._ok_data(result.model_dump(), _("EXPENSE_FOUND"), 200, name)


@router.get("/expenses")
def list_expenses():
    """Get all expenses."""
    db: Session = next(get_db())

    service: IReadService = _get_read_service(db)
    results = service.get_all()

    return Response._ok_data(
        [exp.model_dump() for exp in results],
        _("EXPENSE_LIST"),
        200,
        name
    )


@router.patch("/expenses/<int:expense_id>")
def update_expense(expense_id):
    """Update an expense."""
    db: Session = next(get_db())

    try:
        expense_data = ExpenseUpdate.model_validate(request.json)
    except ValidationError as e:
        return Response._error(_("VALIDATION_ERROR"), e.errors(), 400, name)

    try:
        # Depend only on update interface
        service: IUpdateService = _get_update_service(db)
        result = service.update(expense_id, expense_data)

        if not result:
            return Response._error(_("EXPENSE_NOT_FOUND"), _("NONE"), 404, name)

        return Response._ok_data(result.model_dump(), _("EXPENSE_UPDATED"), 200, name)
    except Exception as e:
        return Response._error(_("DATABASE_ERROR"), str(e), 500, name)


@router.delete("/expenses/<int:expense_id>")
def delete_expense(expense_id):
    """Delete an expense."""
    db: Session = next(get_db())

    try:
        # Depend only on delete interface
        service: IDeleteService = _get_delete_service(db)
        success = service.delete(expense_id)

        if not success:
            return Response._error(_("EXPENSE_NOT_FOUND"), _("NONE"), 404, name)

        return Response._ok_message(_("EXPENSE_DELETED"), 204, name)
    except Exception as e:
        return Response._error(_("DATABASE_ERROR"), str(e), 500, name)


@router.get("/expenses/user/<int:user_id>")
def get_user_expenses(user_id):
    """Get all expenses for a specific user."""
    db: Session = next(get_db())

    try:
        # Depend only on search interface
        service = ExpenseService(db)
        results = service.get_by_user(user_id)

        if not results:
            return Response._error(_("EXPENSE_NOT_FOUND"), _("NONE"), 404, name)

        return Response._ok_data(
            [r.model_dump() for r in results],
            _("EXPENSE_FOUND"),
            200,
            name
        )
    except Exception as e:
        return Response._error(_("DATABASE_ERROR"), str(e), 500, name)
