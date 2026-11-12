"""Router for InvestmentsCategory endpoints following ISP."""
from fastapi import APIRouter, Body, Depends, Query, Request
from typing import Any
from sqlalchemy.orm import Session
from pydantic import ValidationError
from utils.i18n import _

from schemas.investments.investment_category_schema import InvestmentCategoryBase, InvestmentCategoryCreate, InvestmentCategoryUpdate
from schemas.core.export_schema import export_schema

from services.investments.investment_category_service import InvestmentsCategoryService
from db.database import get_db
from services.core.response_service import Response


router = APIRouter()
name = "investment_categories"


def _get_service(db: Session) -> InvestmentsCategoryService:
    """Dependency: service bound to the request session."""
    return InvestmentsCategoryService(db)


@router.post("/investment_categories")
def create(payload: InvestmentCategoryCreate, db: Session = Depends(get_db)):
    try:
        data = InvestmentCategoryCreate.model_validate(payload)
    except ValidationError as e:
        return Response.error(_("VALIDATION_ERROR"), e.errors(), 400, name)
    try:
        service = _get_service(db)
        result = service.create(data)
        return Response.ok_data(result.model_dump(), _("INVESTMENT_CATEGORY_CREATED"), 201, name)
    except Exception as e:
        return Response.error(_("DATABASE_ERROR"), str(e), 500, name)


@router.get("/investment_categories/{id:int}")
def get_by_id(id: int, db: Session = Depends(get_db)):
    service = _get_service(db)
    result = service.get_by_id(id)
    if not result:
        return Response.error(_("INVESTMENT_CATEGORY_NOT_FOUND"), _("NONE"), 404, name)
    return Response.ok_data(result.model_dump(), _("INVESTMENT_CATEGORY_FOUND"), 200, name)


@router.get("/investment_categories")
def list_all(db: Session = Depends(get_db)):
    service = _get_service(db)
    results = service.get_all()
    return Response.ok_data([r.model_dump() for r in results], _("INVESTMENT_CATEGORY_LIST"), 200, name)


@router.patch("/investment_categories/{id:int}")
def update(id: int, payload: InvestmentCategoryUpdate, db: Session = Depends(get_db)):
    try:
        data = InvestmentCategoryUpdate.model_validate(payload)
    except ValidationError as e:
        return Response.error(_("VALIDATION_ERROR"), e.errors(), 400, name)
    try:
        service = _get_service(db)
        result = service.update(id, data)
        if not result:
            return Response.error(_("INVESTMENT_CATEGORY_NOT_FOUND"), _("NONE"), 404, name)
        return Response.ok_data(result.model_dump(), _("INVESTMENT_CATEGORY_UPDATED"), 200, name)
    except Exception as e:
        return Response.error(_("DATABASE_ERROR"), str(e), 500, name)


@router.delete("/investment_categories/{id:int}")
def delete(id: int, db: Session = Depends(get_db)):
    try:
        service = _get_service(db)
        success = service.delete(id)
        if not success:
            return Response.error(_("INVESTMENT_CATEGORY_NOT_FOUND"), _("NONE"), 404, name)
        return esponse.ok_message(_("INVESTMENT_CATEGORY_DELETED"), 204, name)
    except Exception as e:
        return Response.error(_("DATABASE_ERROR"), str(e), 500, name)


@router.get("/meta/investment-category")
def get_meta():
    return export_schema(InvestmentCategoryBase)
