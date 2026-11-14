from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from utils.i18n import _

from schemas.expenses.expense_schema import ExpenseBase, ExpenseCreate, ExpenseUpdate

from services.expenses.expense_service import ExpenseService
from services.core.response_service import Response
from services.auth.auth_dependencies import get_current_user_id

from db.database import get_db
from schemas.core.export_schema import export_schema


router = APIRouter()
name = "expenses"


def _get_service(db: Session) -> ExpenseService:
    """Dependency: ExpenseService bound to the request session."""
    return ExpenseService(db)


@router.post("/expenses")
def create_expense(payload: ExpenseCreate, db: Session = Depends(get_db)):
    """Create a new expense."""
    service = _get_service(db)
    try:
        result = service.create(payload)
    except ValueError as e:
        if str(e) == "DUPLICATE_TRANSACTION":
            return Response.error(_("DUPLICATE_TRANSACTION"), str(e), 409, name)
        # ForeignKey validation errors from service
        return Response.error(_("FK_ERROR"), str(e), 400, name)
    return Response.ok_data(result.model_dump(), _("EXPENSE_CREATED"), 201, name)


@router.post("/expenses/bulk")
def create_expenses_bulk(payload: list[ExpenseCreate], db: Session = Depends(get_db)):
    """Create multiple expenses atomically (duplicates skipped)."""
    service = _get_service(db)
    try:
        result = service.create_batch_atomic(payload)
    except ValueError as e:
        return Response.error(_("FK_ERROR"), str(e), 400, name)
    return Response.ok_data(
        [item.model_dump() for item in result],
        _("EXPENSE_CREATED"),
        201,
        name
    )


@router.get("/expenses/{expense_id:int}")
def get_expense(expense_id: int, db: Session = Depends(get_db)):
    """Get a single expense by ID."""
    service = _get_service(db)
    result = service.get_by_id(expense_id)

    if not result:
        return Response.error(_("EXPENSE_NOT_FOUND"), _("NONE"), 404, name)

    return Response.ok_data(result.model_dump(), _("EXPENSE_FOUND"), 200, name)


@router.get("/expenses")
def list_expenses(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=1000, ge=1, le=5000),
    db: Session = Depends(get_db),
):
    """Get expenses (newest first). Pagination params are optional."""
    service = _get_service(db)
    results = service.get_all(page=page, per_page=per_page)

    return Response.ok_data(
        [exp.model_dump() for exp in results],
        _("EXPENSE_LIST"),
        200,
        name
    )


@router.patch("/expenses/{expense_id:int}")
def update_expense(expense_id: int, payload: ExpenseUpdate, db: Session = Depends(get_db)):
    """Update an expense."""
    service = _get_service(db)
    try:
        result = service.update(expense_id, payload)
    except ValueError as e:
        return Response.error(_("FK_ERROR"), str(e), 400, name)

    if not result:
        return Response.error(_("EXPENSE_NOT_FOUND"), _("NONE"), 404, name)

    return Response.ok_data(result.model_dump(), _("EXPENSE_UPDATED"), 200, name)


@router.delete("/expenses/{expense_id:int}")
def delete_expense(expense_id: int, db: Session = Depends(get_db)):
    """Delete an expense."""
    service = _get_service(db)
    success = service.delete(expense_id)

    if not success:
        return Response.error(_("EXPENSE_NOT_FOUND"), _("NONE"), 404, name)

    return Response.ok_message(_("EXPENSE_DELETED"), 204, name)


@router.get("/expenses/user/{user_id:int}")
def get_user_expenses(
    user_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    """Get all expenses for a specific user (own data only)."""
    if user_id != current_user_id:
        return Response.error(_("AUTH_FORBIDDEN"), _("AUTH_FORBIDDEN"), 403, name)

    service = _get_service(db)
    results = service.get_by_user(user_id)

    if not results:
        return Response.error(_("EXPENSE_NOT_FOUND"), _("NONE"), 404, name)

    return Response.ok_data(
        [r.model_dump() for r in results],
        _("EXPENSE_FOUND"),
        200,
        name
    )


@router.get("/meta/expense")
def get_meta():
    return export_schema(ExpenseBase)
