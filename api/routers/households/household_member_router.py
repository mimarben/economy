"""Router for HouseholdMember endpoints following ISP."""
from fastapi import APIRouter, Body, Depends, Query, Request
from typing import Any
from sqlalchemy.orm import Session
from pydantic import ValidationError
from utils.i18n import _

from schemas.households.household_member_schema import HouseholdMemberBase, HouseholdMemberCreate, HouseholdMemberUpdate
from schemas.core.export_schema import export_schema

from services.households.household_member_service import HouseholdMemberService
from db.database import get_db
from services.core.response_service import Response


router = APIRouter()
name = "household_members"


def _get_service(db: Session) -> HouseholdMemberService:
    """Dependency: service bound to the request session."""
    return HouseholdMemberService(db)


@router.post("/household_members")
def create(payload: HouseholdMemberCreate, db: Session = Depends(get_db)):
    try:
        data = HouseholdMemberCreate.model_validate(payload)
    except ValidationError as e:
        return Response.error(_("VALIDATION_ERROR"), e.errors(), 400, name)
    try:
        service = _get_service(db)
        result = service.create(data)
        return Response.ok_data(result.model_dump(), _("HOUSEHOLD_MEMBER_CREATED"), 201, name)
    except Exception as e:
        return Response.error(_("DATABASE_ERROR"), str(e), 500, name)


@router.get("/household_members/{id:int}")
def get_by_id(id: int, db: Session = Depends(get_db)):
    service = _get_service(db)
    result = service.get_by_id(id)
    if not result:
        return Response.error(_("HOUSEHOLD_MEMBER_NOT_FOUND"), _("NONE"), 404, name)
    return Response.ok_data(result.model_dump(), _("HOUSEHOLD_MEMBER_FOUND"), 200, name)


@router.get("/household_members")
def list_all(db: Session = Depends(get_db)):
    service = _get_service(db)
    results = service.get_all()
    return Response.ok_data([r.model_dump() for r in results], _("HOUSEHOLD_MEMBER_LIST"), 200, name)


@router.patch("/household_members/{id:int}")
def update(id: int, payload: HouseholdMemberUpdate, db: Session = Depends(get_db)):
    try:
        data = HouseholdMemberUpdate.model_validate(payload)
    except ValidationError as e:
        return Response.error(_("VALIDATION_ERROR"), e.errors(), 400, name)
    try:
        service = _get_service(db)
        result = service.update(id, data)
        if not result:
            return Response.error(_("HOUSEHOLD_MEMBER_NOT_FOUND"), _("NONE"), 404, name)
        return Response.ok_data(result.model_dump(), _("HOUSEHOLD_MEMBER_UPDATED"), 200, name)
    except Exception as e:
        return Response.error(_("DATABASE_ERROR"), str(e), 500, name)


@router.delete("/household_members/{id:int}")
def delete(id: int, db: Session = Depends(get_db)):
    try:
        service = _get_service(db)
        success = service.delete(id)
        if not success:
            return Response.error(_("HOUSEHOLD_MEMBER_NOT_FOUND"), _("NONE"), 404, name)
        return esponse.ok_message(_("HOUSEHOLD_MEMBER_DELETED"), 204, name)
    except Exception as e:
        return Response.error(_("DATABASE_ERROR"), str(e), 500, name)


@router.get("/meta/household-member")
def get_meta():
    return export_schema(HouseholdMemberBase)
