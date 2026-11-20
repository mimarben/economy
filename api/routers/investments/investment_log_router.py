"""Router for InvestmentLog endpoints following ISP."""
from fastapi import APIRouter, Body, Depends, Query, Request
from typing import Any
from sqlalchemy.orm import Session
from pydantic import ValidationError
from utils.i18n import _

from schemas.investments.investment_log_schema import InvestmentLogBase, InvestmentLogCreate, InvestmentLogUpdate
from schemas.core.export_schema import export_schema

from services.investments.investment_log_service import InvestmentLogService
from db.database import get_db
from services.core.response_service import Response


router = APIRouter()
name = "investment_logs"


def _get_service(db: Session) -> InvestmentLogService:
    """Dependency: service bound to the request session."""
    return InvestmentLogService(db)


@router.post("/investment_logs")
def create(payload: InvestmentLogCreate, db: Session = Depends(get_db)):
    try:
        data = InvestmentLogCreate.model_validate(payload)
    except ValidationError as e:
        return Response.error(_("VALIDATION_ERROR"), e.errors(), 400, name)
    try:
        service = _get_service(db)
        result = service.create(data)
        return Response.ok_data(result.model_dump(), _("INVESTMENT_LOG_CREATED"), 201, name)
    except Exception as e:
        return Response.error(_("DATABASE_ERROR"), str(e), 500, name)


@router.get("/investment_logs/{id:int}")
def get_by_id(id: int, db: Session = Depends(get_db)):
    service = _get_service(db)
    result = service.get_by_id(id)
    if not result:
        return Response.error(_("INVESTMENT_LOG_NOT_FOUND"), _("NONE"), 404, name)
    return Response.ok_data(result.model_dump(), _("INVESTMENT_LOG_FOUND"), 200, name)


@router.get("/investment_logs")
def list_all(db: Session = Depends(get_db)):
    service = _get_service(db)
    results = service.get_all()
    return Response.ok_data([r.model_dump() for r in results], _("INVESTMENT_LOG_LIST"), 200, name)


@router.patch("/investment_logs/{id:int}")
def update(id: int, payload: InvestmentLogUpdate, db: Session = Depends(get_db)):
    try:
        data = InvestmentLogUpdate.model_validate(payload)
    except ValidationError as e:
        return Response.error(_("VALIDATION_ERROR"), e.errors(), 400, name)
    try:
        service = _get_service(db)
        result = service.update(id, data)
        if not result:
            return Response.error(_("INVESTMENT_LOG_NOT_FOUND"), _("NONE"), 404, name)
        return Response.ok_data(result.model_dump(), _("INVESTMENT_LOG_UPDATED"), 200, name)
    except Exception as e:
        return Response.error(_("DATABASE_ERROR"), str(e), 500, name)


@router.delete("/investment_logs/{id:int}")
def delete(id: int, db: Session = Depends(get_db)):
    try:
        service = _get_service(db)
        success = service.delete(id)
        if not success:
            return Response.error(_("INVESTMENT_LOG_NOT_FOUND"), _("NONE"), 404, name)
        return Response.ok_message(_("INVESTMENT_LOG_DELETED"), 204, name)
    except Exception as e:
        return Response.error(_("DATABASE_ERROR"), str(e), 500, name)


@router.get("/meta/investment-log")
def get_meta():
    return export_schema(InvestmentLogBase)
