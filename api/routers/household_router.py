"""Router for Household endpoints following ISP."""
from flask import Blueprint, request
from sqlalchemy.orm import Session
from pydantic import ValidationError
from flask_babel import _

from schemas.household_schema import HouseholdCreate, HouseholdUpdate
from services.household_service import HouseholdService
from services.interfaces import IReadService, ICreateService, IUpdateService, IDeleteService
from db.database import get_db
from services.response_service import Response


router = Blueprint("households", __name__)
name = "households"


def _get_create_service(db: Session) -> ICreateService:
    return HouseholdService(db)


def _get_read_service(db: Session) -> IReadService:
    return HouseholdService(db)


def _get_update_service(db: Session) -> IUpdateService:
    return HouseholdService(db)


def _get_delete_service(db: Session) -> IDeleteService:
    return HouseholdService(db)


@router.post("/households")
def create():
    db: Session = next(get_db())
    try:
        data = HouseholdCreate.model_validate(request.json)
    except ValidationError as e:
        return Response._error(_("VALIDATION_ERROR"), e.errors(), 400, name)
    try:
        service: ICreateService = _get_create_service(db)
        result = service.create(data)
        return Response._ok_data(result.model_dump(), _("HOUSEHOLD_CREATED"), 201, name)
    except Exception as e:
        return Response._error(_("DATABASE_ERROR"), str(e), 500, name)


@router.get("/households/<int:id>")
def get_by_id(id):
    db: Session = next(get_db())
    service: IReadService = _get_read_service(db)
    result = service.get_by_id(id)
    if not result:
        return Response._error(_("HOUSEHOLD_NOT_FOUND"), _("NONE"), 404, name)
    return Response._ok_data(result.model_dump(), _("HOUSEHOLD_FOUND"), 200, name)


@router.get("/households")
def list_all():
    db: Session = next(get_db())
    service: IReadService = _get_read_service(db)
    results = service.get_all()
    return Response._ok_data([r.model_dump() for r in results], _("HOUSEHOLD_LIST"), 200, name)


@router.patch("/households/<int:id>")
def update(id):
    db: Session = next(get_db())
    try:
        data = HouseholdUpdate.model_validate(request.json)
    except ValidationError as e:
        return Response._error(_("VALIDATION_ERROR"), e.errors(), 400, name)
    try:
        service: IUpdateService = _get_update_service(db)
        result = service.update(id, data)
        if not result:
            return Response._error(_("HOUSEHOLD_NOT_FOUND"), _("NONE"), 404, name)
        return Response._ok_data(result.model_dump(), _("HOUSEHOLD_UPDATED"), 200, name)
    except Exception as e:
        return Response._error(_("DATABASE_ERROR"), str(e), 500, name)


@router.delete("/households/<int:id>")
def delete(id):
    db: Session = next(get_db())
    try:
        service: IDeleteService = _get_delete_service(db)
        success = service.delete(id)
        if not success:
            return Response._error(_("HOUSEHOLD_NOT_FOUND"), _("NONE"), 404, name)
        return Response._ok_message(_("HOUSEHOLD_DELETED"), 204, name)
    except Exception as e:
        return Response._error(_("DATABASE_ERROR"), str(e), 500, name)

