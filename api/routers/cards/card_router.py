"""Router for Source endpoints following ISP."""
from fastapi import APIRouter, Body, Depends, Query, Request
from typing import Any
from sqlalchemy.orm import Session
from pydantic import ValidationError
from utils.i18n import _
from schemas.cards.card_schema import CardBase, CardCreate, CardUpdate
from schemas.core.export_schema import export_schema

from services.cards.card_service import CardService
from services.core.response_service import Response
from services.logs.logger_service import setup_logger

from db.database import get_db

router = APIRouter()
NAME = "cards"

def _get_service(db: Session) -> CardService:
    """Dependency: service bound to the request session."""
    return CardService(db)


@router.post("/cards")
def create(payload: CardCreate, db: Session = Depends(get_db)):
    try:
        data = CardCreate.model_validate(payload)
    except ValidationError as e:
        return Response.error(_("VALIDATION_ERROR"), e.errors(), 400, NAME)

    try:
        service = _get_service(db)
        result = service.create(data)
        return Response.ok_data(result.model_dump(), _("CARD_CREATED"), 201, NAME)
    except Exception as e:
        logger = setup_logger(NAME or "default_error_card")
        logger.exception("Unhandled error in create %s: %s", NAME, str(e))
        return Response.error(_("INTERNAL_ERROR"), _("UNEXPECTED_ERROR"), 500, NAME)


@router.get("/cards/{card_id:int}")
def get_by_id(card_id: int, db: Session = Depends(get_db)):
    service = _get_service(db)
    result = service.get_by_id(card_id)

    if not result:
        return Response.error(_("CARD_NOT_FOUND"), _("NONE"), 404, NAME)

    return Response.ok_data(result.model_dump(), _("CARD_FOUND"), 200, NAME)


@router.get("/cards")
def list_all(request: Request, db: Session = Depends(get_db)):
    service = _get_service(db)

    filters = dict(request.query_params)

    if "account_id" in filters:
        filters["account_id"] = int(filters["account_id"])

    results = service.search(**filters) if filters else service.get_all()

    return Response.ok_data([r.model_dump() for r in results], _("CARD_LIST"), 200, NAME)


@router.patch("/cards/{card_id:int}")
def update(card_id: int, payload: CardUpdate, db: Session = Depends(get_db)):
    try:
        data = CardUpdate.model_validate(payload)
    except ValidationError as e:
        return Response.error(_("VALIDATION_ERROR"), e.errors(), 400, NAME)

    try:
        service = _get_service(db)
        result = service.update(card_id, data)

        if not result:
            return Response.error(_("CARD_NOT_FOUND"), _("NONE"), 404, NAME)

        return Response.ok_data(result.model_dump(), _("CARD_UPDATED"), 200, NAME)

    except Exception as e:
        logger = setup_logger(NAME or "default_error_card")
        logger.exception("Unhandled error in update %s: %s", NAME, str(e))
        return Response.error(_("INTERNAL_ERROR"), _("UNEXPECTED_ERROR"), 500, NAME)


@router.delete("/cards/{card_id:int}")
def delete(card_id: int, db: Session = Depends(get_db)):
    try:
        service = _get_service(db)
        success = service.delete(card_id)

        if not success:
            return Response.error(_("CARD_NOT_FOUND"), _("NONE"), 404, NAME)

        return Response.ok_message(_("CARD_DELETED"), 204, NAME)

    except Exception as e:
        logger = setup_logger(NAME or "default_error_card")
        logger.exception("Unhandled error in delete %s: %s", NAME, str(e))
        return Response.error(_("INTERNAL_ERROR"), _("UNEXPECTED_ERROR"), 500, NAME)


@router.get("/meta/card")
def get_card_meta():
    return export_schema(CardBase)