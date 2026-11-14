"""Router for Income endpoints following ISP."""
from fastapi import APIRouter, Body, Depends, Query, Request
from typing import Any
from sqlalchemy.orm import Session
from pydantic import ValidationError
from utils.i18n import _

from schemas.incomes.income_schema import IncomeBase, IncomeCreate, IncomeUpdate
from schemas.core.export_schema import export_schema

from services.incomes.income_service import IncomeService
from db.database import get_db
from services.core.response_service import Response


router = APIRouter()
name = "incomes"


def _get_service(db: Session) -> IncomeService:
    """Dependency: service bound to the request session."""
    return IncomeService(db)


@router.post("/incomes")
def create(payload: IncomeCreate, db: Session = Depends(get_db)):
    try:
        data = IncomeCreate.model_validate(payload)
    except ValidationError as e:
        return Response.error(_("VALIDATION_ERROR"), e.errors(), 400, name)
    try:
        service = _get_service(db)
        result = service.create(data)
        return Response.ok_data(result.model_dump(), _("INCOME_CREATED"), 201, name)
    except ValueError as e:
        if str(e) == "DUPLICATE_TRANSACTION":
            return Response.error(_("DUPLICATE_TRANSACTION"), str(e), 409, name)
        return Response.error(_("FK_ERROR"), str(e), 400, name)
    except Exception as e:
        return Response.error(_("DATABASE_ERROR"), str(e), 500, name)

@router.post("/incomes/bulk")
def create_bulk(payload: list[IncomeCreate], db: Session = Depends(get_db)):
    if not isinstance(payload, list):
        return Response.error(_("VALIDATION_ERROR"), "REQUEST_BODY_ARRAY_REQUIRED", 400, name)

    try:
        data = [IncomeCreate.model_validate(item) for item in payload]
    except ValidationError as e:
        return Response.error(_("VALIDATION_ERROR"), e.errors(), 400, name)

    try:
        service = IncomeService(db)
        result = service.create_batch_atomic(data)
        return Response.ok_data([r.model_dump() for r in result], _("INCOME_CREATED"), 201, name)
    except ValueError as e:
        return Response.error(_("FK_ERROR"), str(e), 400, name)
    except Exception as e:
        db.rollback()
        return Response.error(_("DATABASE_ERROR"), str(e), 500, name)


@router.get("/incomes/{id:int}")
def get_by_id(id: int, db: Session = Depends(get_db)):
    service = _get_service(db)
    result = service.get_by_id(id)
    if not result:
        return Response.error(_("INCOME_NOT_FOUND"), _("NONE"), 404, name)
    return Response.ok_data(result.model_dump(), _("INCOME_FOUND"), 200, name)


@router.get("/incomes")
def list_all(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=1000, ge=1, le=5000),
    db: Session = Depends(get_db),
):
    """Get incomes (newest first). Pagination params are optional."""
    service = _get_service(db)
    results = service.get_all(page=page, per_page=per_page)
    return Response.ok_data([r.model_dump() for r in results], _("INCOME_LIST"), 200, name)


@router.patch("/incomes/{id:int}")
def update(id: int, payload: IncomeUpdate, db: Session = Depends(get_db)):
    try:
        data = IncomeUpdate.model_validate(payload)
    except ValidationError as e:
        return Response.error(_("VALIDATION_ERROR"), e.errors(), 400, name)
    try:
        service = _get_service(db)
        result = service.update(id, data)
        if not result:
            return Response.error(_("INCOME_NOT_FOUND"), _("NONE"), 404, name)
        return Response.ok_data(result.model_dump(), _("INCOME_UPDATED"), 200, name)
    except Exception as e:
        return Response.error(_("DATABASE_ERROR"), str(e), 500, name)


@router.delete("/incomes/{id:int}")
def delete(id: int, db: Session = Depends(get_db)):
    try:
        service = _get_service(db)
        success = service.delete(id)
        if not success:
            return Response.error(_("INCOME_NOT_FOUND"), _("NONE"), 404, name)
        return Response.ok_message(_("INCOME_DELETED"), 204, name)
    except Exception as e:
        return Response.error(_("DATABASE_ERROR"), str(e), 500, name)


@router.get("/meta/income")
def get_meta():
    return export_schema(IncomeBase)
