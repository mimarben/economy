"""Router for Saving endpoints following ISP."""
from flask import Blueprint, request
from sqlalchemy.orm import Session
from pydantic import ValidationError
from flask_babel import _

from schemas.savings.saving_schema import SavingBase, SavingCreate, SavingUpdate
from schemas.core.export_schema import export_schema

from services.savings.saving_service import SavingService
from services.core.interfaces import IReadService, ICreateService, IUpdateService, IDeleteService
from services.core.response_service import Response

from db.database import get_db


router = Blueprint("savings", __name__)
NAME = "savings"


def _get_create_service(db: Session) -> ICreateService:
    return SavingService(db)


def _get_read_service(db: Session) -> IReadService:
    return SavingService(db)


def _get_update_service(db: Session) -> IUpdateService:
    return SavingService(db)


def _get_delete_service(db: Session) -> IDeleteService:
    return SavingService(db)


@router.post("/savings")
def create():
    db: Session = next(get_db())
    try:
        data = SavingCreate.model_validate(request.json)
    except ValidationError as e:
        return Response.error(_("VALIDATION_ERROR"), e.errors(), 400, NAME)
    try:
        service: ICreateService = _get_create_service(db)
        result = service.create(data)
        return Response.ok_data(result.model_dump(), _("SAVING_CREATED"), 201, NAME)
    except Exception as e:
        return Response.error(_("DATABASE_ERROR"), str(e), 500, NAME)


@router.get("/savings/<int:saving_id>")
def get_by_id(saving_id):
    db: Session = next(get_db())
    service: IReadService = _get_read_service(db)
    result = service.get_by_id(saving_id)
    if not result:
        return Response.error(_("SAVING_NOT_FOUND"), _("NONE"), 404, NAME)
    return Response.ok_data(result.model_dump(), _("SAVING_FOUND"), 200, NAME)


@router.get("/savings")
def list_all():
    db: Session = next(get_db())
    service: IReadService = _get_read_service(db)
    results = service.get_all()
    return Response.ok_data([r.model_dump() for r in results], _("SAVING_LIST"), 200, NAME)


@router.patch("/savings/<int:saving_id>")
def update(saving_id):
    db: Session = next(get_db())
    try:
        data = SavingUpdate.model_validate(request.json)
    except ValidationError as e:
        return Response.error(_("VALIDATION_ERROR"), e.errors(), 400, NAME)
    try:
        service: IUpdateService = _get_update_service(db)
        result = service.update(saving_id, data)
        if not result:
            return Response.error(_("SAVING_NOT_FOUND"), _("NONE"), 404, NAME)
        return Response.ok_data(result.model_dump(), _("SAVING_UPDATED"), 200, NAME)
    except Exception as e:
        return Response.error(_("DATABASE_ERROR"), str(e), 500, NAME)


@router.delete("/savings/<int:saving_id>")
def delete(saving_id):
    db: Session = next(get_db())
    try:
        service: IDeleteService = _get_delete_service(db)
        success = service.delete(saving_id)
        if not success:
            return Response.error(_("SAVING_NOT_FOUND"), _("NONE"), 404, NAME)
        return Response.ok_message(_("SAVING_DELETED"), 204, NAME)
    except Exception as e:
        return Response.error(_("DATABASE_ERROR"), str(e), 500, NAME)


@router.get("/meta/saving")
def get_meta():
    return export_schema(SavingBase)
