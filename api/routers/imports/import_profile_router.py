"""Router for ImportProfile endpoints following ISP."""
from fastapi import APIRouter, Body, Depends, Query, Request
from typing import Any

from sqlalchemy.orm import Session
from pydantic import ValidationError
from utils.i18n import _

from schemas.imports.import_profile_schema import (
    ImportProfileBase,
    ImportProfileCreate,
    ImportProfileUpdate,
)
from schemas.core.export_schema import export_schema

from services.imports.import_profile_service import ImportProfileService
from services.core.response_service import Response
from services.logs.logger_service import setup_logger

from db.database import get_db


router = APIRouter()
NAME = "import_profiles"
logger = setup_logger(NAME)


def get_service(db: Session) -> ImportProfileService:
    return ImportProfileService(db)


def handle_validation(schema, payload):
    try:
        return schema.model_validate(payload), None
    except ValidationError as e:
        return None, Response.error(_("VALIDATION_ERROR"), e.errors(), 400, NAME)


def handle_exception(e: Exception, action: str):
    logger.exception("Unhandled error in %s %s: %s", action, NAME, str(e))
    return Response.error(_("INTERNAL_ERROR"), _("UNEXPECTED_ERROR"), 500, NAME)


@router.post("/import-profiles")
def create(payload: ImportProfileCreate, db: Session = Depends(get_db)):
    data, error = handle_validation(ImportProfileCreate, payload)
    if error:
        return error

    try:
        result = get_service(db).create(data)
        return Response.ok_data(result.model_dump(), _("IMPORT_PROFILE_CREATED"), 201, NAME)
    except Exception as e:
        return handle_exception(e, "create")


@router.get("/import-profiles/{profile_id:int}")
def get_by_id(profile_id: int, db: Session = Depends(get_db)):
    result = get_service(db).get_by_id(profile_id)
    if not result:
        return Response.error(_("IMPORT_PROFILE_NOT_FOUND"), _("NONE"), 404, NAME)

    return Response.ok_data(result.model_dump(), _("IMPORT_PROFILE_FOUND"), 200, NAME)


@router.get("/import-profiles")
def list_all(db: Session = Depends(get_db)):
    results = get_service(db).get_all()
    return Response.ok_data(
        [r.model_dump() for r in results],
        _("IMPORT_PROFILE_LIST"),
        200,
        NAME
    )


@router.patch("/import-profiles/{profile_id:int}")
def update(profile_id: int, payload: ImportProfileUpdate, db: Session = Depends(get_db)):
    data, error = handle_validation(ImportProfileUpdate, payload)
    if error:
        return error

    try:
        result = get_service(db).update(profile_id, data)

        if not result:
            return Response.error(_("IMPORT_PROFILE_NOT_FOUND"), _("NONE"), 404, NAME)

        return Response.ok_data(result.model_dump(), _("IMPORT_PROFILE_UPDATED"), 200, NAME)

    except Exception as e:
        return handle_exception(e, "update")


@router.delete("/import-profiles/{profile_id:int}")
def delete(profile_id: int, db: Session = Depends(get_db)):
    try:
        success = get_service(db).delete(profile_id)

        if not success:
            return Response.error(_("IMPORT_PROFILE_NOT_FOUND"), _("NONE"), 404, NAME)

        return Response.ok_message(_("IMPORT_PROFILE_DELETED"), 204, NAME)

    except Exception as e:
        return handle_exception(e, "delete")


@router.get("/meta/import-profile")
def get_meta():
    return export_schema(ImportProfileBase)