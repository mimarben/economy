"""Router for Investment endpoints following ISP."""
from fastapi import APIRouter, Body, Depends, Query, Request
from typing import Any
from sqlalchemy.orm import Session
from pydantic import ValidationError
from utils.i18n import _

from schemas.investments.investment_schema import InvestmentBase, InvestmentCreate, InvestmentUpdate
from schemas.core.export_schema import export_schema

from services.investments.investment_service import InvestmentService
from db.database import get_db
from services.core.response_service import Response


router = APIRouter()
name = "investments"


def _get_service(db: Session) -> InvestmentService:
    """Dependency: service bound to the request session."""
    return InvestmentService(db)


@router.post("/investments")
def create(payload: InvestmentCreate, db: Session = Depends(get_db)):
    try:
        data = InvestmentCreate.model_validate(payload)
    except ValidationError as e:
        return Response.error(_("VALIDATION_ERROR"), e.errors(), 400, name)
    try:
        service = _get_service(db)
        result = service.create(data)
        return Response.ok_data(result.model_dump(), _("INVESTMENT_CREATED"), 201, name)
    except ValueError as e:
        if str(e) == "DUPLICATE_TRANSACTION":
            return Response.error(_("DUPLICATE_TRANSACTION"), str(e), 409, name)
        return Response.error(_("VALIDATION_ERROR"), str(e), 400, name)
    except Exception as e:
        return Response.error(_("DATABASE_ERROR"), str(e), 500, name)


@router.get("/investments/{id:int}")
def get_by_id(id: int, db: Session = Depends(get_db)):
    service = _get_service(db)
    result = service.get_by_id(id)
    if not result:
        return Response.error(_("INVESTMENT_NOT_FOUND"), _("NONE"), 404, name)
    return Response.ok_data(result.model_dump(), _("INVESTMENT_FOUND"), 200, name)


@router.get("/investments")
def list_all(db: Session = Depends(get_db)):
    service = _get_service(db)
    results = service.get_all()
    return Response.ok_data([r.model_dump() for r in results], _("INVESTMENT_LIST"), 200, name)


@router.patch("/investments/{id:int}")
def update(id: int, payload: InvestmentUpdate, db: Session = Depends(get_db)):
    try:
        data = InvestmentUpdate.model_validate(payload)
    except ValidationError as e:
        return Response.error(_("VALIDATION_ERROR"), e.errors(), 400, name)
    try:
        service = _get_service(db)
        result = service.update(id, data)
        if not result:
            return Response.error(_("INVESTMENT_NOT_FOUND"), _("NONE"), 404, name)
        return Response.ok_data(result.model_dump(), _("INVESTMENT_UPDATED"), 200, name)
    except Exception as e:
        return Response.error(_("DATABASE_ERROR"), str(e), 500, name)


@router.delete("/investments/{id:int}")
def delete(id: int, db: Session = Depends(get_db)):
    try:
        service = _get_service(db)
        success = service.delete(id)
        if not success:
            return Response.error(_("INVESTMENT_NOT_FOUND"), _("NONE"), 404, name)
        return esponse.ok_message(_("INVESTMENT_DELETED"), 204, name)
    except Exception as e:
        return Response.error(_("DATABASE_ERROR"), str(e), 500, name)


@router.get("/meta/investment")
def get_meta():
    return export_schema(InvestmentBase)
