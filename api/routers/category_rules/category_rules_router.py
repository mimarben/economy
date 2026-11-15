"""Router for CategoryRule endpoints following ISP."""
from fastapi import APIRouter, Body, Depends, Query, Request
from typing import Any

from sqlalchemy.orm import Session
from pydantic import ValidationError
from utils.i18n import _

from schemas.rules.category_rule_schema import (
    CategoryRuleCreate,
    CategoryRuleUpdate,
    CategorizeBatchRequest,
)
from services.rules.categorization_service import CategoryRuleService, CategorizationService
from db.database import get_db
from services.core.response_service import Response


router = APIRouter()
name = "category_rules"


def _get_service(db: Session) -> CategoryRuleService:
    """Dependency: service bound to the request session."""
    return CategoryRuleService(db)


@router.post("/category_rules")
def create(payload: CategoryRuleCreate, db: Session = Depends(get_db)):
    """Create a new categorization rule."""
    try:
        data = CategoryRuleCreate.model_validate(payload)
    except ValidationError as e:
        return Response.error(_("VALIDATION_ERROR"), e.errors(), 400, name)
    try:
        service = _get_service(db)
        result = service.create(data)
        return Response.ok_data(result.model_dump(), _("CATEGORY_RULE_CREATED"), 201, name)
    except ValueError as e:
        return Response.error(_("INVALID_DATA"), str(e), 400, name)
    except Exception as e:
        return Response.error(_("DATABASE_ERROR"), str(e), 500, name)


@router.get("/category_rules/{id:int}")
def get_by_id(id: int, db: Session = Depends(get_db)):
    """Get a specific categorization rule by ID."""
    try:
        service = _get_service(db)
        result = service.get_by_id(id)
        if not result:
            return Response.error(_("CATEGORY_RULE_NOT_FOUND"), _("NONE"), 404, name)
        return Response.ok_data(result.model_dump(), _("CATEGORY_RULE_FOUND"), 200, name)
    except Exception as e:
        return Response.error(_("DATABASE_ERROR"), str(e), 500, name)


@router.get("/category_rules")
def list_all(db: Session = Depends(get_db)):
    """List all categorization rules."""
    try:
        service = _get_service(db)
        results = service.get_all()
        return Response.ok_data([r.model_dump() for r in results], _("CATEGORY_RULE_LIST"), 200, name)
    except Exception as e:
        return Response.error(_("DATABASE_ERROR"), str(e), 500, name)


@router.post("/category_rules/categorize")
def categorize_batch(payload: CategorizeBatchRequest, db: Session = Depends(get_db)):
    """Categorize a batch of transactions with the same engine the import uses.

    Applies category rules + source rules + ignore flag in one pass, so the
    import preview shows exactly what the import will store.
    """
    try:
        service = CategorizationService(db)
        items = [t.model_dump() for t in payload.transactions]
        results = service.categorize_batch(items)
        return Response.ok_data(results, _("CATEGORY_RULE_LIST"), 200, name)
    except Exception as e:
        return Response.error(_("DATABASE_ERROR"), str(e), 500, name)


@router.get("/category_rules/by_type/{transaction_type}")
def get_active_by_type(transaction_type: str, db: Session = Depends(get_db)):
    """Get active rules for a specific transaction type."""
    try:
        service = CategoryRuleService(db)
        results = service.get_active_by_type(transaction_type)
        return Response.ok_data([r.model_dump() for r in results], _("CATEGORY_RULE_LIST"), 200, name)
    except ValueError as e:
        return Response.error(_("INVALID_DATA"), str(e), 400, name)
    except Exception as e:
        return Response.error(_("DATABASE_ERROR"), str(e), 500, name)


@router.patch("/category_rules/{id:int}")
def update(id: int, payload: CategoryRuleUpdate, db: Session = Depends(get_db)):
    """Update a categorization rule."""
    try:
        data = CategoryRuleUpdate.model_validate(payload)
    except ValidationError as e:
        return Response.error(_("VALIDATION_ERROR"), e.errors(), 400, name)
    try:
        service = _get_service(db)
        result = service.update(id, data)
        if not result:
            return Response.error(_("CATEGORY_RULE_NOT_FOUND"), _("NONE"), 404, name)
        return Response.ok_data(result.model_dump(), _("CATEGORY_RULE_UPDATED"), 200, name)
    except ValueError as e:
        return Response.error(_("INVALID_DATA"), str(e), 400, name)
    except Exception as e:
        return Response.error(_("DATABASE_ERROR"), str(e), 500, name)


@router.delete("/category_rules/{id:int}")
def delete(id: int, db: Session = Depends(get_db)):
    """Delete a categorization rule."""
    try:
        service = _get_service(db)
        if not service.delete(id):
            return Response.error(_("CATEGORY_RULE_NOT_FOUND"), _("NONE"), 404, name)
        return Response.ok_data(None, _("CATEGORY_RULE_DELETED"), 200, name)
    except Exception as e:
        return Response.error(_("DATABASE_ERROR"), str(e), 500, name)
