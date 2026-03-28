"""Router for CategoryRule endpoints following ISP."""

from flask import Blueprint, request
from sqlalchemy.orm import Session
from pydantic import ValidationError
from flask_babel import _

from schemas.category_rules.category_rule_schema import CategoryRuleCreate, CategoryRuleUpdate
from services.category_rules.categorization_service import CategoryRuleService
from services.core.interfaces import IReadService, ICreateService, IUpdateService, IDeleteService
from db.database import get_db
from services.core.response_service import Response


router = Blueprint("category_rules", __name__)
name = "category_rules"


def _get_create_service(db: Session) -> ICreateService:
    return CategoryRuleService(db)


def _get_read_service(db: Session) -> IReadService:
    return CategoryRuleService(db)


def _get_update_service(db: Session) -> IUpdateService:
    return CategoryRuleService(db)


def _get_delete_service(db: Session) -> IDeleteService:
    return CategoryRuleService(db)


@router.post("/category_rules")
def create():
    """Create a new categorization rule."""
    db: Session = next(get_db())
    try:
        data = CategoryRuleCreate.model_validate(request.json)
    except ValidationError as e:
        return Response._error(_("VALIDATION_ERROR"), e.errors(), 400, name)
    try:
        service: ICreateService = _get_create_service(db)
        result = service.create(data)
        return Response._ok_data(result.model_dump(), _("CATEGORY_RULE_CREATED"), 201, name)
    except ValueError as e:
        return Response._error(_("INVALID_DATA"), str(e), 400, name)
    except Exception as e:
        return Response._error(_("DATABASE_ERROR"), str(e), 500, name)


@router.get("/category_rules/<int:id>")
def get_by_id(id):
    """Get a specific categorization rule by ID."""
    db: Session = next(get_db())
    try:
        service: IReadService = _get_read_service(db)
        result = service.get_by_id(id)
        if not result:
            return Response._error(_("CATEGORY_RULE_NOT_FOUND"), _("NONE"), 404, name)
        return Response._ok_data(result.model_dump(), _("CATEGORY_RULE_FOUND"), 200, name)
    except Exception as e:
        return Response._error(_("DATABASE_ERROR"), str(e), 500, name)


@router.get("/category_rules")
def list_all():
    """List all categorization rules."""
    db: Session = next(get_db())
    try:
        service: IReadService = _get_read_service(db)
        results = service.get_all()
        return Response._ok_data([r.model_dump() for r in results], _("CATEGORY_RULE_LIST"), 200, name)
    except Exception as e:
        return Response._error(_("DATABASE_ERROR"), str(e), 500, name)


@router.get("/category_rules/by_type/<string:transaction_type>")
def get_active_by_type(transaction_type: str):
    """Get active rules for a specific transaction type."""
    db: Session = next(get_db())
    try:
        service = CategoryRuleService(db)
        results = service.get_active_by_type(transaction_type)
        return Response._ok_data([r.model_dump() for r in results], _("CATEGORY_RULE_LIST"), 200, name)
    except ValueError as e:
        return Response._error(_("INVALID_DATA"), str(e), 400, name)
    except Exception as e:
        return Response._error(_("DATABASE_ERROR"), str(e), 500, name)


@router.patch("/category_rules/<int:id>")
def update(id):
    """Update a categorization rule."""
    db: Session = next(get_db())
    try:
        data = CategoryRuleUpdate.model_validate(request.json)
    except ValidationError as e:
        return Response._error(_("VALIDATION_ERROR"), e.errors(), 400, name)
    try:
        service: IUpdateService = _get_update_service(db)
        result = service.update(id, data)
        if not result:
            return Response._error(_("CATEGORY_RULE_NOT_FOUND"), _("NONE"), 404, name)
        return Response._ok_data(result.model_dump(), _("CATEGORY_RULE_UPDATED"), 200, name)
    except ValueError as e:
        return Response._error(_("INVALID_DATA"), str(e), 400, name)
    except Exception as e:
        return Response._error(_("DATABASE_ERROR"), str(e), 500, name)


@router.delete("/category_rules/<int:id>")
def delete(id):
    """Delete a categorization rule."""
    db: Session = next(get_db())
    try:
        service: IDeleteService = _get_delete_service(db)
        if not service.delete(id):
            return Response._error(_("CATEGORY_RULE_NOT_FOUND"), _("NONE"), 404, name)
        return Response._ok_data(None, _("CATEGORY_RULE_DELETED"), 200, name)
    except Exception as e:
        return Response._error(_("DATABASE_ERROR"), str(e), 500, name)
