"""Router for ExpensesCategory endpoints following ISP."""
from flask import Blueprint, request
from sqlalchemy.orm import Session
from pydantic import ValidationError
from flask_babel import _

from schemas.expenses.expense_category_schema import ExpenseCategoryCreate, ExpenseCategoryUpdate
from services.expenses.expense_category_service import ExpensesCategoryService
from services.core.interfaces import IReadService, ICreateService, IUpdateService, IDeleteService
from db.database import get_db
from services.core.response_service import Response


router = Blueprint("expenses_categories", __name__)
name = "expenses_categories"


def _get_create_service(db: Session) -> ICreateService:
    return ExpensesCategoryService(db)

def _get_read_service(db: Session) -> IReadService:
    return ExpensesCategoryService(db)

def _get_update_service(db: Session) -> IUpdateService:
    return ExpensesCategoryService(db)

def _get_delete_service(db: Session) -> IDeleteService:
    return ExpensesCategoryService(db)


@router.post("/expenses_categories")
def create():
    db: Session = next(get_db())
    try:
        data = ExpenseCategoryCreate.model_validate(request.json)
    except ValidationError as e:
        return Response._error(_("VALIDATION_ERROR"), e.errors(), 400, name)
    try:
        service: ICreateService = _get_create_service(db)
        result = service.create(data)
        return Response._ok_data(result.model_dump(), _("EXPENSE_CATEGORY_CREATED"), 201, name)
    except ValueError as e:
        return Response._error(_("INVALID_DATA"), str(e), 400, name)
    except Exception as e:
        return Response._error(_("DATABASE_ERROR"), str(e), 500, name)


@router.get("/expenses_categories/<int:id>")
def get_by_id(id):
    db: Session = next(get_db())
    try:
        service: IReadService = _get_read_service(db)
        result = service.get_by_id(id)
        if not result:
            return Response._error(_("EXPENSE_CATEGORY_NOT_FOUND"), _("NONE"), 404, name)
        return Response._ok_data(result.model_dump(), _("EXPENSE_CATEGORY_FOUND"), 200, name)
    except Exception as e:
        return Response._error(_("DATABASE_ERROR"), str(e), 500, name)


@router.get("/expenses_categories")
def list_all():
    db: Session = next(get_db())
    try:
        service: IReadService = _get_read_service(db)
        results = service.get_all()
        return Response._ok_data([r.model_dump() for r in results], _("EXPENSE_CATEGORY_LIST"), 200, name)
    except Exception as e:
        return Response._error(_("DATABASE_ERROR"), str(e), 500, name)


@router.patch("/expenses_categories/<int:id>")
def update(id):
    db: Session = next(get_db())
    try:
        data = ExpenseCategoryUpdate.model_validate(request.json)
    except ValidationError as e:
        return Response._error(_("VALIDATION_ERROR"), e.errors(), 400, name)
    try:
        service: IUpdateService = _get_update_service(db)
        result = service.update(id, data)
        if not result:
            return Response._error(_("EXPENSE_CATEGORY_NOT_FOUND"), _("NONE"), 404, name)
        return Response._ok_data(result.model_dump(), _("EXPENSE_CATEGORY_UPDATED"), 200, name)
    except Exception as e:
        return Response._error(_("DATABASE_ERROR"), str(e), 500, name)


@router.delete("/expenses_categories/<int:id>")
def delete(id):
    db: Session = next(get_db())
    try:
        service: IDeleteService = _get_delete_service(db)
        success = service.delete(id)
        if not success:
            return Response._error(_("EXPENSE_CATEGORY_NOT_FOUND"), _("NONE"), 404, name)
        return Response._ok_message(_("EXPENSE_CATEGORY_DELETED"), 204, name)
    except Exception as e:
        return Response._error(_("DATABASE_ERROR"), str(e), 500, name)
