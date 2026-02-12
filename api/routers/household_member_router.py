"""Router for HouseholdMember endpoints following ISP."""
from flask import Blueprint, request
from sqlalchemy.orm import Session
from pydantic import ValidationError
from flask_babel import _

from schemas.household_member_schema import HouseholdMemberCreate, HouseholdMemberUpdate
from services.household_member_service import HouseholdMemberService
from services.interfaces import IReadService, ICreateService, IUpdateService, IDeleteService
from db.database import get_db
from services.response_service import Response


router = Blueprint("household_members", __name__)
name = "household_members"


def _get_create_service(db: Session) -> ICreateService:
    return HouseholdMemberService(db)


def _get_read_service(db: Session) -> IReadService:
    return HouseholdMemberService(db)


def _get_update_service(db: Session) -> IUpdateService:
    return HouseholdMemberService(db)


def _get_delete_service(db: Session) -> IDeleteService:
    return HouseholdMemberService(db)


@router.post("/household_members")
def create():
    db: Session = next(get_db())
    try:
        data = HouseholdMemberCreate.model_validate(request.json)
    except ValidationError as e:
        return Response._error(_("VALIDATION_ERROR"), e.errors(), 400, name)
    try:
        service: ICreateService = _get_create_service(db)
        result = service.create(data)
        return Response._ok_data(result.model_dump(), _("HOUSEHOLD_MEMBER_CREATED"), 201, name)
    except Exception as e:
        return Response._error(_("DATABASE_ERROR"), str(e), 500, name)


@router.get("/household_members/<int:id>")
def get_by_id(id):
    db: Session = next(get_db())
    service: IReadService = _get_read_service(db)
    result = service.get_by_id(id)
    if not result:
        return Response._error(_("HOUSEHOLD_MEMBER_NOT_FOUND"), _("NONE"), 404, name)
    return Response._ok_data(result.model_dump(), _("HOUSEHOLD_MEMBER_FOUND"), 200, name)


@router.get("/household_members")
def list_all():
    db: Session = next(get_db())
    service: IReadService = _get_read_service(db)
    results = service.get_all()
    return Response._ok_data([r.model_dump() for r in results], _("HOUSEHOLD_MEMBER_LIST"), 200, name)


@router.patch("/household_members/<int:id>")
def update(id):
    db: Session = next(get_db())
    try:
        data = HouseholdMemberUpdate.model_validate(request.json)
    except ValidationError as e:
        return Response._error(_("VALIDATION_ERROR"), e.errors(), 400, name)
    try:
        service: IUpdateService = _get_update_service(db)
        result = service.update(id, data)
        if not result:
            return Response._error(_("HOUSEHOLD_MEMBER_NOT_FOUND"), _("NONE"), 404, name)
        return Response._ok_data(result.model_dump(), _("HOUSEHOLD_MEMBER_UPDATED"), 200, name)
    except Exception as e:
        return Response._error(_("DATABASE_ERROR"), str(e), 500, name)


@router.delete("/household_members/<int:id>")
def delete(id):
    db: Session = next(get_db())
    try:
        service: IDeleteService = _get_delete_service(db)
        success = service.delete(id)
        if not success:
            return Response._error(_("HOUSEHOLD_MEMBER_NOT_FOUND"), _("NONE"), 404, name)
        return Response._ok_message(_("HOUSEHOLD_MEMBER_DELETED"), 204, name)
    except Exception as e:
        return Response._error(_("DATABASE_ERROR"), str(e), 500, name)
