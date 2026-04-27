"""Router for SourceRule endpoints following ISP."""

from flask import Blueprint, request
from sqlalchemy.orm import Session
from pydantic import ValidationError
from flask_babel import _

from schemas.category_rules.source_rule_schema import SourceRuleCreate, SourceRuleUpdate
from services.category_rules.source_rule_service import SourceRuleService
from services.core.interfaces import IReadService, ICreateService, IUpdateService, IDeleteService
from db.database import get_db
from services.core.response_service import Response


router = Blueprint("source_rules", __name__)
name = "source_rules"


def _get_create_service(db: Session) -> ICreateService:
    return SourceRuleService(db)


def _get_read_service(db: Session) -> IReadService:
    return SourceRuleService(db)


def _get_update_service(db: Session) -> IUpdateService:
    return SourceRuleService(db)


def _get_delete_service(db: Session) -> IDeleteService:
    return SourceRuleService(db)


@router.post("/source_rules")
def create():
    """Create a new source rule association."""
    db: Session = next(get_db())
    try:
        data = SourceRuleCreate.model_validate(request.json)
    except ValidationError as e:
        return Response.error(_("VALIDATION_ERROR"), e.errors(), 400, name)
    try:
        service: ICreateService = _get_create_service(db)
        result = service.create(data)
        return Response.ok_data(result.model_dump(), _("SOURCE_RULE_CREATED"), 201, name)
    except ValueError as e:
        return Response.error(_("INVALID_DATA"), str(e), 400, name)
    except Exception as e:
        return Response.error(_("DATABASE_ERROR"), str(e), 500, name)


@router.get("/source_rules/<int:id>")
def get_by_id(id):
    """Get a specific source rule by ID."""
    db: Session = next(get_db())
    try:
        service: IReadService = _get_read_service(db)
        result = service.get_by_id(id)
        if not result:
            return Response.error(_("SOURCE_RULE_NOT_FOUND"), _("NONE"), 404, name)
        return Response.ok_data(result.model_dump(), _("SOURCE_RULE_FOUND"), 200, name)
    except Exception as e:
        return Response.error(_("DATABASE_ERROR"), str(e), 500, name)


@router.get("/source_rules")
def list_all():
    """List all source rules."""
    db: Session = next(get_db())
    try:
        service: IReadService = _get_read_service(db)
        results = service.get_all()
        return Response.ok_data([r.model_dump() for r in results], _("SOURCE_RULE_LIST"), 200, name)
    except Exception as e:
        return Response.error(_("DATABASE_ERROR"), str(e), 500, name)


@router.get("/source_rules/by_category_rule/<int:category_rule_id>")
def get_active_by_category_rule(category_rule_id: int):
    """Get active source rules for a specific category rule."""
    db: Session = next(get_db())
    try:
        service = SourceRuleService(db)
        results = service.get_active_by_category_rule(category_rule_id)
        return Response.ok_data([r.model_dump() for r in results], _("SOURCE_RULE_LIST"), 200, name)
    except Exception as e:
        return Response.error(_("DATABASE_ERROR"), str(e), 500, name)


@router.patch("/source_rules/<int:id>")
def update(id):
    """Update a source rule."""
    db: Session = next(get_db())
    try:
        data = SourceRuleUpdate.model_validate(request.json)
    except ValidationError as e:
        return Response.error(_("VALIDATION_ERROR"), e.errors(), 400, name)
    try:
        service: IUpdateService = _get_update_service(db)
        result = service.update(id, data)
        if not result:
            return Response.error(_("SOURCE_RULE_NOT_FOUND"), _("NONE"), 404, name)
        return Response.ok_data(result.model_dump(), _("SOURCE_RULE_UPDATED"), 200, name)
    except ValueError as e:
        return Response.error(_("INVALID_DATA"), str(e), 400, name)
    except Exception as e:
        return Response.error(_("DATABASE_ERROR"), str(e), 500, name)


@router.delete("/source_rules/<int:id>")
def delete(id):
    """Delete a source rule."""
    db: Session = next(get_db())
    try:
        service: IDeleteService = _get_delete_service(db)
        if not service.delete(id):
            return Response.error(_("SOURCE_RULE_NOT_FOUND"), _("NONE"), 404, name)
        return Response.ok_data(None, _("SOURCE_RULE_DELETED"), 200, name)
    except Exception as e:
        return Response.error(_("DATABASE_ERROR"), str(e), 500, name)
