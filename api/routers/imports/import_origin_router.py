"""Router for ImportOrigin endpoints following ISP."""
from fastapi import APIRouter, Body, Depends, Query, Request
from typing import Any

from sqlalchemy.orm import Session
from pydantic import ValidationError
from utils.i18n import _

from schemas.imports.import_origin_schema import (
    ImportOriginBase,
    ImportOriginCreate,
    ImportOriginUpdate,
)
from schemas.core.export_schema import export_schema

from services.imports.import_origin_service import ImportOriginService
from services.core.response_service import Response
from services.logs.logger_service import setup_logger

from db.database import get_db


router = APIRouter()
NAME = "import_origins"
logger = setup_logger(NAME)


def _get_service(db: Session) -> ImportOriginService:
    """Dependency: service bound to the request session."""
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
def create(payload: ImportOriginCreate, db: Session = Depends(get_db)):
    data, error = handle_validation(ImportOriginCreate, payload)
    if error:
        return error

    try:
        service = _get_service(db)
        result = service.create(data)
        return Response.ok_data(result.model_dump(), _("IMPORT_PROFILE_CREATED"), 201, NAME)
    except Exception as e:
        return handle_exception(e, "create")


@router.get("/import-origins/{origin_id:int}")
def get_by_id(origin_id: int, db: Session = Depends(get_db)):
    service = _get_service(db)
    result = service.get_by_id(origin_id)
    if not result:
        return Response.error(_("IMPORT_PROFILE_NOT_FOUND"), _("NONE"), 404, NAME)

    return Response.ok_data(result.model_dump(), _("IMPORT_PROFILE_FOUND"), 200, NAME)


@router.get("/import-origins")
def list_all(db: Session = Depends(get_db)):
    service = _get_service(db)
    results = service.get_all()
    return Response.ok_data(
        [r.model_dump() for r in results],
        _("IMPORT_PROFILE_LIST"),
        200,
        NAME
    )


@router.patch("/import-origins/{origin_id:int}")
def update(origin_id: int, payload: ImportOriginUpdate, db: Session = Depends(get_db)):
    data, error = handle_validation(ImportOriginUpdate, payload)
    if error:
        return error

    try:
        service = _get_service(db)
        result = service.update(origin_id, data)

        if not result:
            return Response.error(_("IMPORT_PROFILE_NOT_FOUND"), _("NONE"), 404, NAME)

        return Response.ok_data(result.model_dump(), _("IMPORT_PROFILE_UPDATED"), 200, NAME)

    except Exception as e:
        return handle_exception(e, "update")


@router.delete("/import-origins/{origin_id:int}")
def delete(origin_id: int, db: Session = Depends(get_db)):
    try:
        service = _get_service(db)
        success = service.delete(origin_id)

        if not success:
            return Response.error(_("IMPORT_PROFILE_NOT_FOUND"), _("NONE"), 404, NAME)

        return Response.ok_message(_("IMPORT_PROFILE_DELETED"), 204, NAME)

    except Exception as e:
        return handle_exception(e, "delete")


@router.get("/meta/import-origins")
def get_meta():
    return export_schema(ImportOriginBase)


@router.get("/meta/import-origin")
def get_meta_alias():
    return export_schema(ImportOriginBase)
