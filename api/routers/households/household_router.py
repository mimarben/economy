"""Router for Household endpoints following ISP."""
from fastapi import APIRouter, Body, Depends, Query, Request
from typing import Any
from sqlalchemy.orm import Session
from pydantic import ValidationError
from utils.i18n import _

from schemas.households.household_schema import HouseholdBase, HouseholdCreate, HouseholdUpdate
from schemas.core.export_schema import export_schema

from services.households.household_service import HouseholdService
from db.database import get_db
from services.core.response_service import Response


router = APIRouter()
name = "households"


def _get_service(db: Session) -> HouseholdService:
    """Dependency: service bound to the request session."""
    return HouseholdService(db)


@router.post("/households")
def create(payload: HouseholdCreate, db: Session = Depends(get_db)):
    try:
        data = HouseholdCreate.model_validate(payload)
    except ValidationError as e:
        return Response.error(_("VALIDATION_ERROR"), e.errors(), 400, name)
    try:
        service = _get_service(db)
        result = service.create(data)
        return Response.ok_data(result.model_dump(), _("HOUSEHOLD_CREATED"), 201, name)
    except Exception as e:
        return Response.error(_("DATABASE_ERROR"), str(e), 500, name)


@router.get("/households/{id:int}")
def get_by_id(id: int, db: Session = Depends(get_db)):
    service = _get_service(db)
    result = service.get_by_id(id)
    if not result:
        return Response.error(_("HOUSEHOLD_NOT_FOUND"), _("NONE"), 404, name)
    return Response.ok_data(result.model_dump(), _("HOUSEHOLD_FOUND"), 200, name)


@router.get("/households")
def list_all(db: Session = Depends(get_db)):
    service = _get_service(db)
    results = service.get_all()
    return Response.ok_data([r.model_dump() for r in results], _("HOUSEHOLD_LIST"), 200, name)


@router.patch("/households/{id:int}")
def update(id: int, payload: HouseholdUpdate, db: Session = Depends(get_db)):
    try:
        data = HouseholdUpdate.model_validate(payload)
    except ValidationError as e:
        return Response.error(_("VALIDATION_ERROR"), e.errors(), 400, name)
    try:
        service = _get_service(db)
        result = service.update(id, data)
        if not result:
            return Response.error(_("HOUSEHOLD_NOT_FOUND"), _("NONE"), 404, name)
        return Response.ok_data(result.model_dump(), _("HOUSEHOLD_UPDATED"), 200, name)
    except Exception as e:
        return Response.error(_("DATABASE_ERROR"), str(e), 500, name)


@router.delete("/households/{id:int}")
def delete(id: int, db: Session = Depends(get_db)):
    try:
        service = _get_service(db)
        success = service.delete(id)
        if not success:
            return Response.error(_("HOUSEHOLD_NOT_FOUND"), _("NONE"), 404, name)
        return esponse.ok_message(_("HOUSEHOLD_DELETED"), 204, name)
    except Exception as e:
        return Response.error(_("DATABASE_ERROR"), str(e), 500, name)



@router.get("/meta/household")
def get_meta():
    return export_schema(HouseholdBase)
