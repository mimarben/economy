"""Router for SourceRule endpoints following ISP."""
from fastapi import APIRouter, Body, Depends, Query, Request
from typing import Any

from sqlalchemy.orm import Session
from pydantic import ValidationError
from utils.i18n import _

from schemas.rules.source_rule_schema import SourceRuleBase, SourceRuleCreate, SourceRuleUpdate
from schemas.core.export_schema import export_schema
from services.rules.source_rule_service import SourceRuleService
from db.database import get_db
from services.core.response_service import Response


router = APIRouter()
name = "source_rules"


def _get_service(db: Session) -> SourceRuleService:
    """Dependency: service bound to the request session."""
    return SourceRuleService(db)


@router.post("/source_rules")
def create(payload: SourceRuleCreate, db: Session = Depends(get_db)):
    """Create a new source rule association."""
    try:
        data = SourceRuleCreate.model_validate(payload)
    except ValidationError as e:
        return Response.error(_("VALIDATION_ERROR"), e.errors(), 400, name)
    try:
        service = _get_service(db)
        result = service.create(data)
        return Response.ok_data(result.model_dump(), _("SOURCE_RULE_CREATED"), 201, name)
    except ValueError as e:
        return Response.error(_("INVALID_DATA"), str(e), 400, name)
    except Exception as e:
        return Response.error(_("DATABASE_ERROR"), str(e), 500, name)


@router.get("/source_rules/{id:int}")
def get_by_id(id: int, db: Session = Depends(get_db)):
    """Get a specific source rule by ID."""
    try:
        service = _get_service(db)
        result = service.get_by_id(id)
        if not result:
            return Response.error(_("SOURCE_RULE_NOT_FOUND"), _("NONE"), 404, name)
        return Response.ok_data(result.model_dump(), _("SOURCE_RULE_FOUND"), 200, name)
    except Exception as e:
        return Response.error(_("DATABASE_ERROR"), str(e), 500, name)


@router.get("/source_rules")
def list_all(db: Session = Depends(get_db)):
    """List all source rules."""
    try:
        service = _get_service(db)
        results = service.get_all()
        return Response.ok_data([r.model_dump() for r in results], _("SOURCE_RULE_LIST"), 200, name)
    except Exception as e:
        return Response.error(_("DATABASE_ERROR"), str(e), 500, name)


@router.get("/source_rules/by_type/{transaction_type}")
def get_active_by_type(transaction_type: str, db: Session = Depends(get_db)):
    """Get active source rules for a specific transaction type."""
    try:
        service = SourceRuleService(db)
        results = service.get_active_by_type(transaction_type)
        return Response.ok_data([r.model_dump() for r in results], _("SOURCE_RULE_LIST"), 200, name)
    except ValueError as e:
        return Response.error(_("INVALID_DATA"), str(e), 400, name)
    except Exception as e:
        return Response.error(_("DATABASE_ERROR"), str(e), 500, name)


@router.patch("/source_rules/{id:int}")
def update(id: int, payload: SourceRuleUpdate, db: Session = Depends(get_db)):
    """Update a source rule."""
    try:
        data = SourceRuleUpdate.model_validate(payload)
    except ValidationError as e:
        return Response.error(_("VALIDATION_ERROR"), e.errors(), 400, name)
    try:
        service = _get_service(db)
        result = service.update(id, data)
        if not result:
            return Response.error(_("SOURCE_RULE_NOT_FOUND"), _("NONE"), 404, name)
        return Response.ok_data(result.model_dump(), _("SOURCE_RULE_UPDATED"), 200, name)
    except ValueError as e:
        return Response.error(_("INVALID_DATA"), str(e), 400, name)
    except Exception as e:
        return Response.error(_("DATABASE_ERROR"), str(e), 500, name)


@router.delete("/source_rules/{id:int}")
def delete(id: int, db: Session = Depends(get_db)):
    """Delete a source rule."""
    try:
        service = _get_service(db)
        if not service.delete(id):
            return Response.error(_("SOURCE_RULE_NOT_FOUND"), _("NONE"), 404, name)
        return Response.ok_data(None, _("SOURCE_RULE_DELETED"), 200, name)
    except Exception as e:
        return Response.error(_("DATABASE_ERROR"), str(e), 500, name)


@router.get("/meta/source_rule")
def get_source_rule_meta():
    """Return form field metadata for SourceRule."""
    return export_schema(SourceRuleBase)
