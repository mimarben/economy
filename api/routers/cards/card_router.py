"""Router for Source endpoints following ISP."""
from flask import Blueprint, request
from sqlalchemy.orm import Session
from pydantic import ValidationError
from flask_babel import _

from schemas.cards.card_schema import CardBase, CardCreate, CardUpdate, CardRead
from schemas.core.export_schema import export_schema

from services.cards.card_service import CardService
from services.core.interfaces import IReadService, ICreateService, IUpdateService, IDeleteService
from services.core.response_service import Response
from services.logs.logger_service import setup_logger

from db.database import get_db

router = Blueprint("cards", __name__)
NAME = "cards"

def _get_create_service(db: Session) -> ICreateService:
    return CardService(db)


def _get_read_service(db: Session) -> IReadService:
    return CardService(db)


def _get_update_service(db: Session) -> IUpdateService:
    return CardService(db)


def _get_delete_service(db: Session) -> IDeleteService:
    return CardService(db)


@router.post("/cards")
def create():
    db: Session = next(get_db())
    try:
        data = CardCreate.model_validate(request.json)
    except ValidationError as e:
        return Response.error(_("VALIDATION_ERROR"), e.errors(), 400, NAME)

    try:
        service: ICreateService = _get_create_service(db)
        result = service.create(data)
        return Response.ok_data(result.model_dump(), _("CARD_CREATED"), 201, NAME)
    except Exception as e:
        logger = setup_logger(NAME or "default_error_card")
        logger.exception("Unhandled error in create %s: %s", NAME, str(e))
        return Response.error(_("INTERNAL_ERROR"), _("UNEXPECTED_ERROR"), 500, NAME)


@router.get("/cards/<int:card_id>")
def get_by_id(card_id: int):
    db: Session = next(get_db())
    service: IReadService = _get_read_service(db)
    result = service.get_by_id(card_id)

    if not result:
        return Response.error(_("CARD_NOT_FOUND"), _("NONE"), 404, NAME)

    return Response.ok_data(result.model_dump(), _("CARD_FOUND"), 200, NAME)


@router.get("/cards")
def list_all():
    db: Session = next(get_db())
    service: IReadService = _get_read_service(db)

    account_id = request.args.get("account_id", type=int)

    if account_id:
        results = service.get_by_account(account_id)  # 🔥 útil para tu caso
    else:
        results = service.get_all()

    return Response.ok_data([r.model_dump() for r in results], _("CARD_LIST"), 200, NAME)


@router.patch("/cards/<int:card_id>")
def update(card_id: int):
    db: Session = next(get_db())
    try:
        data = CardUpdate.model_validate(request.json)
    except ValidationError as e:
        return Response.error(_("VALIDATION_ERROR"), e.errors(), 400, NAME)

    try:
        service: IUpdateService = _get_update_service(db)
        result = service.update(card_id, data)

        if not result:
            return Response.error(_("CARD_NOT_FOUND"), _("NONE"), 404, NAME)

        return Response.ok_data(result.model_dump(), _("CARD_UPDATED"), 200, NAME)

    except Exception as e:
        logger = setup_logger(NAME or "default_error_card")
        logger.exception("Unhandled error in update %s: %s", NAME, str(e))
        return Response.error(_("INTERNAL_ERROR"), _("UNEXPECTED_ERROR"), 500, NAME)


@router.delete("/cards/<int:card_id>")
def delete(card_id: int):
    db: Session = next(get_db())
    try:
        service: IDeleteService = _get_delete_service(db)
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