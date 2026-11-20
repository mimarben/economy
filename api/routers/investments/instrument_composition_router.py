"""Router for InstrumentComposition endpoints following ISP."""
from fastapi import APIRouter, Body, Depends, Query, Request
from typing import Any
from sqlalchemy.orm import Session
from pydantic import ValidationError
from utils.i18n import _

from schemas.investments.instrument_composition_schema import (
    InstrumentCompositionBase, 
    InstrumentCompositionCreate, 
    InstrumentCompositionUpdate
)
from schemas.core.export_schema import export_schema

from services.investments.instrument_composition_service import InstrumentCompositionService
from db.database import get_db
from services.core.response_service import Response


router = APIRouter()
name = "instrument_compositions"


def _get_service(db: Session) -> InstrumentCompositionService:
    """Dependency: service bound to the request session."""
    return InstrumentCompositionService(db)


@router.post("/instrument_compositions")
def create(payload: InstrumentCompositionCreate, db: Session = Depends(get_db)):
    try:
        data = InstrumentCompositionCreate.model_validate(payload)
    except ValidationError as e:
        return Response.error(_("VALIDATION_ERROR"), e.errors(), 400, name)
    try:
        service = _get_service(db)
        result = service.create(data)
        return Response.ok_data(result.model_dump(), _("INSTRUMENT_COMPOSITION_CREATED"), 201, name)
    except Exception as e:
        return Response.error(_("DATABASE_ERROR"), str(e), 500, name)


@router.get("/instrument_compositions/{id:int}")
def get_by_id(id: int, db: Session = Depends(get_db)):
    service = _get_service(db)
    result = service.get_by_id(id)
    if not result:
        return Response.error(_("INSTRUMENT_COMPOSITION_NOT_FOUND"), _("NONE"), 404, name)
    return Response.ok_data(result.model_dump(), _("INSTRUMENT_COMPOSITION_FOUND"), 200, name)


@router.get("/instrument_compositions")
def list_all(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    parent_id: int = Query(None, description="Filter by parent instrument ID"),
    child_id: int = Query(None, description="Filter by child instrument ID"),
    db: Session = Depends(get_db)
):
    service = _get_service(db)
    if parent_id:
        results = service.get_by_parent(parent_id)
    elif child_id:
        results = service.get_by_child(child_id)
    else:
        results = service.get_all(page=page, per_page=per_page)
    return Response.ok_data([r.model_dump() for r in results], _("INSTRUMENT_COMPOSITION_LIST"), 200, name)


@router.patch("/instrument_compositions/{id:int}")
def update(id: int, payload: InstrumentCompositionUpdate, db: Session = Depends(get_db)):
    try:
        data = InstrumentCompositionUpdate.model_validate(payload)
    except ValidationError as e:
        return Response.error(_("VALIDATION_ERROR"), e.errors(), 400, name)
    try:
        service = _get_service(db)
        result = service.update(id, data)
        if not result:
            return Response.error(_("INSTRUMENT_COMPOSITION_NOT_FOUND"), _("NONE"), 404, name)
        return Response.ok_data(result.model_dump(), _("INSTRUMENT_COMPOSITION_UPDATED"), 200, name)
    except Exception as e:
        return Response.error(_("DATABASE_ERROR"), str(e), 500, name)


@router.delete("/instrument_compositions/{id:int}")
def delete(id: int, db: Session = Depends(get_db)):
    try:
        service = _get_service(db)
        success = service.delete(id)
        if not success:
            return Response.error(_("INSTRUMENT_COMPOSITION_NOT_FOUND"), _("NONE"), 404, name)
        return Response.ok_message(_("INSTRUMENT_COMPOSITION_DELETED"), 204, name)
    except Exception as e:
        return Response.error(_("DATABASE_ERROR"), str(e), 500, name)


@router.get("/meta/instrument-composition")
def get_meta():
    return export_schema(InstrumentCompositionBase)
