"""Router for SavingLog endpoints following ISP."""
from fastapi import APIRouter, Body, Depends, Query, Request
from typing import Any
from sqlalchemy.orm import Session
from pydantic import ValidationError
from utils.i18n import _

from schemas.savings.saving_log_schema import SavingLogBase, SavingLogCreate, SavingLogUpdate
from schemas.core.export_schema import export_schema

from services.savings.saving_log_service import SavingLogService
from db.database import get_db
from services.core.response_service import Response


router = APIRouter()
name = "saving_logs"


def _get_service(db: Session) -> SavingLogService:
    """Dependency: service bound to the request session."""
    return SavingLogService(db)


@router.post("/saving_logs")
def create(payload: SavingLogCreate, db: Session = Depends(get_db)):
    try:
        data = SavingLogCreate.model_validate(payload)
    except ValidationError as e:
        return Response.error(_("VALIDATION_ERROR"), e.errors(), 400, name)
    try:
        service = _get_service(db)
        result = service.create(data)
        return Response.ok_data(result.model_dump(), _("SAVING_LOG_CREATED"), 201, name)
    except Exception as e:
        return Response.error(_("DATABASE_ERROR"), str(e), 500, name)


@router.get("/saving_logs/{id:int}")
def get_by_id(id: int, db: Session = Depends(get_db)):
    service = _get_service(db)
    result = service.get_by_id(id)
    if not result:
        return Response.error(_("SAVING_LOG_NOT_FOUND"), _("NONE"), 404, name)
    return Response.ok_data(result.model_dump(), _("SAVING_LOG_FOUND"), 200, name)


@router.get("/saving_logs")
def list_all(db: Session = Depends(get_db)):
    service = _get_service(db)
    results = service.get_all()
    return Response.ok_data([r.model_dump() for r in results], _("SAVING_LOG_LIST"), 200, name)


@router.patch("/saving_logs/{id:int}")
def update(id: int, payload: SavingLogUpdate, db: Session = Depends(get_db)):
    try:
        data = SavingLogUpdate.model_validate(payload)
    except ValidationError as e:
        return Response.error(_("VALIDATION_ERROR"), e.errors(), 400, name)
    try:
        service = _get_service(db)
        result = service.update(id, data)
        if not result:
            return Response.error(_("SAVING_LOG_NOT_FOUND"), _("NONE"), 404, name)
        return Response.ok_data(result.model_dump(), _("SAVING_LOG_UPDATED"), 200, name)
    except Exception as e:
        return Response.error(_("DATABASE_ERROR"), str(e), 500, name)


@router.delete("/saving_logs/{id:int}")
def delete(id: int, db: Session = Depends(get_db)):
    try:
        service = _get_service(db)
        success = service.delete(id)
        if not success:
            return Response.error(_("SAVING_LOG_NOT_FOUND"), _("NONE"), 404, name)
        return Response.ok_message(_("SAVING_LOG_DELETED"), 204, name)
    except Exception as e:
        return Response.error(_("DATABASE_ERROR"), str(e), 500, name)


@router.get("/meta/saving-log")
def get_meta():
    return export_schema(SavingLogBase)
