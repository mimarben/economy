"""Router for ImportOrigin endpoints following ISP."""

from flask import Blueprint, request
from sqlalchemy.orm import Session
from pydantic import ValidationError
from flask_babel import _

from schemas.imports.import_origin_schema import (
    ImportOriginBase,
    ImportOriginCreate,
    ImportOriginUpdate,
)
from schemas.core.export_schema import export_schema

from services.core.interfaces import IReadService, IUpdateService,ICreateService, IUpdateService, IDeleteService
from services.imports.import_origin_service import ImportOriginService
from services.core.response_service import Response
from services.logs.logger_service import setup_logger

from db.database import get_db


router = Blueprint("import_origins", __name__)
NAME = "import_origins"
logger = setup_logger(NAME)


def _get_create_service(db: Session) -> ICreateService:
    return ImportOriginService(db)


def _get_read_service(db: Session) -> IReadService:
    return ImportOriginService(db)


def _get_update_service(db: Session) -> IUpdateService:
    return ImportOriginService(db)


def _get_delete_service(db: Session) -> IDeleteService:
    return ImportOriginService(db)


def handle_validation(schema, payload):
    try:
        return schema.model_validate(payload), None
    except ValidationError as e:
        return None, Response.error(_("VALIDATION_ERROR"), e.errors(), 400, NAME)


def handle_exception(e: Exception, action: str):
    logger.exception("Unhandled error in %s %s: %s", action, NAME, str(e))
    return Response.error(_("INTERNAL_ERROR"), _("UNEXPECTED_ERROR"), 500, NAME)


@router.post("/import-origins")
def create():
    db: Session = next(get_db())

    data, error = handle_validation(ImportOriginCreate, request.json)
    if error:
        return error

    try:
        service: ICreateService = _get_create_service(db)
        result = service.create(data)
        return Response.ok_data(result.model_dump(), _("IMPORT_PROFILE_CREATED"), 201, NAME)
    except Exception as e:
        return handle_exception(e, "create")


@router.get("/import-origins/<int:origin_id>")
def get_by_id(origin_id: int):
    db: Session = next(get_db())
    service: IReadService = _get_read_service(db)
    result = service.get_by_id(origin_id)
    if not result:
        return Response.error(_("IMPORT_PROFILE_NOT_FOUND"), _("NONE"), 404, NAME)

    return Response.ok_data(result.model_dump(), _("IMPORT_PROFILE_FOUND"), 200, NAME)


@router.get("/import-origins")
def list_all():
    db: Session = next(get_db())
    service: IReadService = _get_read_service(db)
    results = service.get_all()
    return Response.ok_data(
        [r.model_dump() for r in results],
        _("IMPORT_PROFILE_LIST"),
        200,
        NAME
    )


@router.patch("/import-origins/<int:origin_id>")
def update(origin_id: int):
    db: Session = next(get_db())

    data, error = handle_validation(ImportOriginUpdate, request.json)
    if error:
        return error

    try:
        service: IUpdateService = _get_update_service(db)
        result = service.update(origin_id, data)

        if not result:
            return Response.error(_("IMPORT_PROFILE_NOT_FOUND"), _("NONE"), 404, NAME)

        return Response.ok_data(result.model_dump(), _("IMPORT_PROFILE_UPDATED"), 200, NAME)

    except Exception as e:
        return handle_exception(e, "update")


@router.delete("/import-origins/<int:origin_id>")
def delete(origin_id: int):
    db: Session = next(get_db())

    try:
        service: IDeleteService = _get_delete_service(db)
        success = service.delete(origin_id)

        if not success:
            return Response.error(_("IMPORT_PROFILE_NOT_FOUND"), _("NONE"), 404, NAME)

        return Response.ok_message(_("IMPORT_PROFILE_DELETED"), 204, NAME)

    except Exception as e:
        return handle_exception(e, "delete")


@router.get("/meta/import-profile")
def get_meta():
    return export_schema(ImportOriginBase)