"""Router for Instrument endpoints following ISP."""
from fastapi import APIRouter, Body, Depends, Query, Request
from typing import Any
from sqlalchemy.orm import Session
from pydantic import ValidationError
from utils.i18n import _

from schemas.investments.instrument_schema import InstrumentBase, InstrumentCreate, InstrumentUpdate
from schemas.core.export_schema import export_schema

from services.investments.instrument_service import InstrumentService
from db.database import get_db
from services.core.response_service import Response
from services.auth.auth_dependencies import get_current_user_id


router = APIRouter()
name = "instruments"


def _get_service(db: Session) -> InstrumentService:
    """Dependency: service bound to the request session."""
    return InstrumentService(db)


@router.post("/instruments")
def create(payload: InstrumentCreate, db: Session = Depends(get_db)):
    try:
        data = InstrumentCreate.model_validate(payload)
    except ValidationError as e:
        return Response.error(_("VALIDATION_ERROR"), e.errors(), 400, name)
    try:
        service = _get_service(db)
        result = service.create(data)
        return Response.ok_data(result.model_dump(), _("INSTRUMENT_CREATED"), 201, name)
    except Exception as e:
        return Response.error(_("DATABASE_ERROR"), str(e), 500, name)


@router.get("/instruments/{id:int}")
def get_by_id(id: int, db: Session = Depends(get_db)):
    service = _get_service(db)
    result = service.get_by_id(id)
    if not result:
        return Response.error(_("INSTRUMENT_NOT_FOUND"), _("NONE"), 404, name)
    return Response.ok_data(result.model_dump(), _("INSTRUMENT_FOUND"), 200, name)


@router.get("/instruments")
def list_all(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    service = _get_service(db)
    results = service.get_all(page=page, per_page=per_page)
    return Response.ok_data([r.model_dump() for r in results], _("INSTRUMENT_LIST"), 200, name)


@router.get("/instruments/search")
def search_instruments(
    isin: str = Query(None, description="Search by ISIN"),
    name: str = Query(None, description="Search by name (partial match)"),
    ticker: str = Query(None, description="Search by ticker"),
    provider: str = Query(None, description="Search by provider"),
    provider_id: str = Query(None, description="Search by provider identifier"),
    db: Session = Depends(get_db)
):
    """Search instruments by various criteria. Returns all matches (no auto-selection)."""
    service = _get_service(db)
    
    results = []
    if isin:
        results.extend(service.search_by_isin(isin))
    if name:
        results.extend(service.search_by_name(name))
    if ticker:
        results.extend(service.search_by_ticker(ticker))
    if provider and provider_id:
        results.extend(service.search_by_provider_identifier(provider, provider_id))
    
    # Remove duplicates while preserving order
    seen = set()
    unique_results = []
    for r in results:
        key = r.id
        if key not in seen:
            seen.add(key)
            unique_results.append(r)
    
    return Response.ok_data([r.model_dump() for r in unique_results], _("INSTRUMENT_SEARCH_RESULTS"), 200, name)


@router.patch("/instruments/{id:int}")
def update(id: int, payload: InstrumentUpdate, db: Session = Depends(get_db)):
    try:
        data = InstrumentUpdate.model_validate(payload)
    except ValidationError as e:
        return Response.error(_("VALIDATION_ERROR"), e.errors(), 400, name)
    try:
        service = _get_service(db)
        result = service.update(id, data)
        if not result:
            return Response.error(_("INSTRUMENT_NOT_FOUND"), _("NONE"), 404, name)
        return Response.ok_data(result.model_dump(), _("INSTRUMENT_UPDATED"), 200, name)
    except Exception as e:
        return Response.error(_("DATABASE_ERROR"), str(e), 500, name)


@router.delete("/instruments/{id:int}")
def delete(id: int, db: Session = Depends(get_db)):
    try:
        service = _get_service(db)
        success = service.delete(id)
        if not success:
            return Response.error(_("INSTRUMENT_NOT_FOUND"), _("NONE"), 404, name)
        return Response.ok_message(_("INSTRUMENT_DELETED"), 204, name)
    except Exception as e:
        return Response.error(_("DATABASE_ERROR"), str(e), 500, name)


@router.post("/instruments/{instrument_id:int}/attach-investment/{investment_id:int}")
def attach_investment(
    instrument_id: int, 
    investment_id: int, 
    db: Session = Depends(get_db)
):
    """Attach an existing investment to an instrument."""
    service = _get_service(db)
    result = service.attach_investment(instrument_id, investment_id)
    if not result:
        return Response.error(_("INSTRUMENT_OR_INVESTMENT_NOT_FOUND"), _("NONE"), 404, name)
    return Response.ok_data(result.model_dump(), _("INSTRUMENT_INVESTMENT_ATTACHED"), 200, name)


@router.get("/meta/instrument")
def get_meta():
    return export_schema(InstrumentBase)
