"""Router for Source endpoints following ISP."""
from flask import Blueprint, request
from sqlalchemy.orm import Session
from pydantic import ValidationError
from flask_babel import _

from schemas.finance.source_schema import SourceCreate, SourceUpdate
from services.finance.source_service import SourceService
from services.core.interfaces import IReadService, ICreateService, IUpdateService, IDeleteService
from db.database import get_db
from services.core.response_service import Response


router = Blueprint("sources", __name__)
name = "sources"


def _get_create_service(db: Session) -> ICreateService:
    return SourceService(db)


def _get_read_service(db: Session) -> IReadService:
    return SourceService(db)


def _get_update_service(db: Session) -> IUpdateService:
    return SourceService(db)


def _get_delete_service(db: Session) -> IDeleteService:
    return SourceService(db)


@router.post("/sources")
def create():
    db: Session = next(get_db())
    try:
        data = SourceCreate.model_validate(request.json)
    except ValidationError as e:
        return Response._error(_("VALIDATION_ERROR"), e.errors(), 400, name)
    try:
        service: ICreateService = _get_create_service(db)
        result = service.create(data)
        return Response._ok_data(result.model_dump(), _("SOURCE_CREATED"), 201, name)
    except Exception as e:
        return Response._error(_("DATABASE_ERROR"), str(e), 500, name)


@router.get("/sources/<int:id>")
def get_by_id(id):
    db: Session = next(get_db())
    service: IReadService = _get_read_service(db)
    result = service.get_by_id(id)
    if not result:
        return Response._error(_("SOURCE_NOT_FOUND"), _("NONE"), 404, name)
    return Response._ok_data(result.model_dump(), _("SOURCE_FOUND"), 200, name)


@router.get("/sources")
def list_all():
    db: Session = next(get_db())
    service: IReadService = _get_read_service(db)
    results = service.get_all()
    return Response._ok_data([r.model_dump() for r in results], _("SOURCE_LIST"), 200, name)


@router.patch("/sources/<int:id>")
def update(id):
    db: Session = next(get_db())
    try:
        data = SourceUpdate.model_validate(request.json)
    except ValidationError as e:
        return Response._error(_("VALIDATION_ERROR"), e.errors(), 400, name)
    try:
        service: IUpdateService = _get_update_service(db)
        result = service.update(id, data)
        if not result:
            return Response._error(_("SOURCE_NOT_FOUND"), _("NONE"), 404, name)
        return Response._ok_data(result.model_dump(), _("SOURCE_UPDATED"), 200, name)
    except Exception as e:
        return Response._error(_("DATABASE_ERROR"), str(e), 500, name)


@router.delete("/sources/<int:id>")
def delete(id):
    db: Session = next(get_db())
    try:
        service: IDeleteService = _get_delete_service(db)
        success = service.delete(id)
        if not success:
            return Response._error(_("SOURCE_NOT_FOUND"), _("NONE"), 404, name)
        return Response._ok_message(_("SOURCE_DELETED"), 204, name)
    except Exception as e:
        return Response._error(_("DATABASE_ERROR"), str(e), 500, name)
