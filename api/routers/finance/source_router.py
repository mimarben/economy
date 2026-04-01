"""Router for Source endpoints following ISP."""
from flask import Blueprint, request
from sqlalchemy.orm import Session
from pydantic import ValidationError
from flask_babel import _

from schemas.finance.source_schema import SourceBase, SourceCreate, SourceUpdate
from schemas.core.export_schema import export_schema

from services.finance.source_service import SourceService
from services.core.interfaces import IReadService, ICreateService, IUpdateService, IDeleteService
from services.core.response_service import Response
from services.logs.logger_service import setup_logger

from db.database import get_db


router = Blueprint("sources", __name__)
NAME = "sources"


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
        return Response.error(_("VALIDATION_ERROR"), e.errors(), 400, NAME)
    try:
        service: ICreateService = _get_create_service(db)
        result = service.create(data)
        return Response.ok_data(result.model_dump(), _("SOURCE_CREATED"), 201, NAME)
    except Exception as e:
        logger = setup_logger(NAME or "default_error_source")
        logger.exception("Unhandled error in create %s: %s", NAME, str(e))
        return Response.error(_("INTERNAL_ERROR"), _("UNEXPECTED_ERROR"), 500, NAME)


@router.get("/sources/<int:source_id>")
def get_by_id(source_id: int):
    db: Session = next(get_db())
    service: IReadService = _get_read_service(db)
    result = service.get_by_id(source_id)
    if not result:
        return Response.error(_("SOURCE_NOT_FOUND"), _("NONE"), 404, NAME)
    return Response.ok_data(result.model_dump(), _("SOURCE_FOUND"), 200, NAME)


@router.get("/sources")
def list_all():
    db: Session = next(get_db())
    service: IReadService = _get_read_service(db)
    results = service.get_all()
    return Response.ok_data([r.model_dump() for r in results], _("SOURCE_LIST"), 200, NAME)


@router.get("/sources/suggest")
def suggest_source():
    db: Session = next(get_db())
    source_service = SourceService(db)

    category_id = request.args.get('category_id', type=int)
    transaction_type = request.args.get('type', type=str)

    if not category_id or not transaction_type:
        return Response.error(_("INVALID_PARAMETERS"), _("SOURCE_SUGGEST_INVALID_PARAMS"), 400, NAME)

    try:
        suggested = source_service.suggest_source(category_id, transaction_type)
        if not suggested:
            return Response.error(_("SOURCE_NOT_FOUND"), _("NONE"), 404, NAME)
        return Response.ok_data(suggested.model_dump(), _("SOURCE_SUGGESTED"), 200, NAME)
    except Exception as e:
        logger = setup_logger(NAME or "default_error_source")
        logger.exception("Unhandled error in update %s: %s", NAME, str(e))
        return Response.error(_("INTERNAL_ERROR"), _("UNEXPECTED_ERROR"), 500, NAME)


@router.patch("/sources/<int:source_id>")
def update(source_id: int):
    db: Session = next(get_db())
    try:
        data = SourceUpdate.model_validate(request.json)
    except ValidationError as e:
        return Response.error(_("VALIDATION_ERROR"), e.errors(), 400, NAME)
    try:
        service: IUpdateService = _get_update_service(db)
        result = service.update(source_id, data)
        if not result:
            return Response.error(_("SOURCE_NOT_FOUND"), _("NONE"), 404, NAME)
        return Response.ok_data(result.model_dump(), _("SOURCE_UPDATED"), 200, NAME)
    except Exception as e:
        logger = setup_logger(NAME or "default_error_source")
        logger.exception("Unhandled error in update %s: %s", NAME, str(e))
        return Response.error(_("INTERNAL_ERROR"), _("UNEXPECTED_ERROR"), 500, NAME)


@router.delete("/sources/<int:id>")
def delete(source_id: int):
    db: Session = next(get_db())
    try:
        service: IDeleteService = _get_delete_service(db)
        success = service.delete(source_id)
        if not success:
            return Response.error(_("SOURCE_NOT_FOUND"), _("NONE"), 404, NAME)
        return Response.ok_message(_("SOURCE_DELETED"), 204, NAME)
    except Exception as e:
        logger = setup_logger(NAME or "default_error_source")
        logger.exception("Unhandled error in delete %s: %s", NAME, str(e))
        return Response.error(_("INTERNAL_ERROR"), _("UNEXPECTED_ERROR"), 500, NAME)

@router.get("/meta/source")
def get_source_meta():
    return export_schema(SourceBase)
