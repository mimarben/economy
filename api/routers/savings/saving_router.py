"""Router for Saving endpoints following ISP."""
from fastapi import APIRouter, Body, Depends, Query, Request
from typing import Any
from sqlalchemy.orm import Session
from pydantic import ValidationError
from utils.i18n import _

from schemas.savings.saving_schema import SavingBase, SavingCreate, SavingUpdate
from schemas.core.export_schema import export_schema

from services.savings.saving_service import SavingService
from services.core.response_service import Response

from db.database import get_db


router = APIRouter()
NAME = "savings"


def _get_service(db: Session) -> SavingService:
    """Dependency: service bound to the request session."""
    return SavingService(db)


@router.post("/savings")
def create(payload: SavingCreate, db: Session = Depends(get_db)):
    try:
        data = SavingCreate.model_validate(payload)
    except ValidationError as e:
        return Response.error(_("VALIDATION_ERROR"), e.errors(), 400, NAME)
    try:
        service = _get_service(db)
        result = service.create(data)
        return Response.ok_data(result.model_dump(), _("SAVING_CREATED"), 201, NAME)
    except Exception as e:
        return Response.error(_("DATABASE_ERROR"), str(e), 500, NAME)


@router.get("/savings/{saving_id:int}")
def get_by_id(saving_id: int, db: Session = Depends(get_db)):
    service = _get_service(db)
    result = service.get_by_id(saving_id)
    if not result:
        return Response.error(_("SAVING_NOT_FOUND"), _("NONE"), 404, NAME)
    return Response.ok_data(result.model_dump(), _("SAVING_FOUND"), 200, NAME)


@router.get("/savings")
def list_all(db: Session = Depends(get_db)):
    service = _get_service(db)
    results = service.get_all()
    return Response.ok_data([r.model_dump() for r in results], _("SAVING_LIST"), 200, NAME)


@router.patch("/savings/{saving_id:int}")
def update(saving_id: int, payload: SavingUpdate, db: Session = Depends(get_db)):
    try:
        data = SavingUpdate.model_validate(payload)
    except ValidationError as e:
        return Response.error(_("VALIDATION_ERROR"), e.errors(), 400, NAME)
    try:
        service = _get_service(db)
        result = service.update(saving_id, data)
        if not result:
            return Response.error(_("SAVING_NOT_FOUND"), _("NONE"), 404, NAME)
        return Response.ok_data(result.model_dump(), _("SAVING_UPDATED"), 200, NAME)
    except Exception as e:
        return Response.error(_("DATABASE_ERROR"), str(e), 500, NAME)


@router.delete("/savings/{saving_id:int}")
def delete(saving_id: int, db: Session = Depends(get_db)):
    try:
        service = _get_service(db)
        success = service.delete(saving_id)
        if not success:
            return Response.error(_("SAVING_NOT_FOUND"), _("NONE"), 404, NAME)
        return Response.ok_message(_("SAVING_DELETED"), 204, NAME)
    except Exception as e:
        return Response.error(_("DATABASE_ERROR"), str(e), 500, NAME)


@router.get("/meta/saving")
def get_meta():
    return export_schema(SavingBase)
