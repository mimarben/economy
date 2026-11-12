"""Router for ExpensesCategory endpoints following ISP."""
from fastapi import APIRouter, Body, Depends, Query, Request
from typing import Any
from sqlalchemy.orm import Session
from pydantic import ValidationError
from utils.i18n import _

from schemas.expenses.expense_category_schema import ExpenseCategoryBase, ExpenseCategoryCreate, ExpenseCategoryUpdate
from schemas.core.export_schema import export_schema

from services.expenses.expense_category_service import ExpensesCategoryService
from db.database import get_db
from services.core.response_service import Response


router = APIRouter()
name = "expenses_categories"


def _get_service(db: Session) -> ExpensesCategoryService:
    """Dependency: service bound to the request session."""
    return ExpensesCategoryService(db)


@router.post("/expenses_categories")
def create(payload: ExpenseCategoryCreate, db: Session = Depends(get_db)):
    try:
        data = ExpenseCategoryCreate.model_validate(payload)
    except ValidationError as e:
        return Response.error(_("VALIDATION_ERROR"), e.errors(), 400, name)
    try:
        service = _get_service(db)
        result = service.create(data)
        return Response.ok_data(result.model_dump(), _("EXPENSE_CATEGORY_CREATED"), 201, name)
    except ValueError as e:
        return Response.error(_("INVALID_DATA"), str(e), 400, name)
    except Exception as e:
        return Response.error(_("DATABASE_ERROR"), str(e), 500, name)


@router.get("/expenses_categories/{id:int}")
def get_by_id(id: int, db: Session = Depends(get_db)):
    try:
        service = _get_service(db)
        result = service.get_by_id(id)
        if not result:
            return Response.error(_("EXPENSE_CATEGORY_NOT_FOUND"), _("NONE"), 404, name)
        return Response.ok_data(result.model_dump(), _("EXPENSE_CATEGORY_FOUND"), 200, name)
    except Exception as e:
        return Response.error(_("DATABASE_ERROR"), str(e), 500, name)


@router.get("/expenses_categories")
def list_all(db: Session = Depends(get_db)):
    try:
        service = _get_service(db)
        results = service.get_all()
        return Response.ok_data([r.model_dump() for r in results], _("EXPENSE_CATEGORY_LIST"), 200, name)
    except Exception as e:
        return Response.error(_("DATABASE_ERROR"), str(e), 500, name)


@router.patch("/expenses_categories/{id:int}")
def update(id: int, payload: ExpenseCategoryUpdate, db: Session = Depends(get_db)):
    try:
        data = ExpenseCategoryUpdate.model_validate(payload)
    except ValidationError as e:
        return Response.error(_("VALIDATION_ERROR"), e.errors(), 400, name)
    try:
        service = _get_service(db)
        result = service.update(id, data)
        if not result:
            return Response.error(_("EXPENSE_CATEGORY_NOT_FOUND"), _("NONE"), 404, name)
        return Response.ok_data(result.model_dump(), _("EXPENSE_CATEGORY_UPDATED"), 200, name)
    except Exception as e:
        return Response.error(_("DATABASE_ERROR"), str(e), 500, name)


@router.delete("/expenses_categories/{id:int}")
def delete(id: int, db: Session = Depends(get_db)):
    try:
        service = _get_service(db)
        success = service.delete(id)
        if not success:
            return Response.error(_("EXPENSE_CATEGORY_NOT_FOUND"), _("NONE"), 404, name)
        return Response.ok_message(_("EXPENSE_CATEGORY_DELETED"), 204, name)
    except Exception as e:
        return Response.error(_("DATABASE_ERROR"), str(e), 500, name)


@router.get("/meta/expense-category")
def get_meta():
    return export_schema(ExpenseCategoryBase)
