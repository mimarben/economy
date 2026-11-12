"""Router for Account endpoints following ISP - Dependency Inversion Principle."""
from fastapi import APIRouter, Body, Depends, Query, Request
from typing import Any
from sqlalchemy.orm import Session
from pydantic import ValidationError
from utils.i18n import _

from models.finance.account_model import Account
from schemas.finance.account_schema import AccountBase, AccountCreate, AccountUpdate

from schemas.core.export_schema import export_schema

from services.finance.account_service import AccountService
from services.core.response_service import Response
from services.logs.logger_service import setup_logger

from db.database import get_db


router = APIRouter()
NAME = "accounts"


def _get_service(db: Session) -> AccountService:
    """Dependency: service bound to the request session."""
    return AccountService(db)


@router.post("/accounts")
def create(payload: AccountCreate, db: Session = Depends(get_db)):
    """Create a new account."""
    try:
        data = AccountCreate.model_validate(payload)
    except ValidationError as e:
        return Response.error(_("VALIDATION_ERROR"), e.errors(), 400, NAME)

    try:
        service = _get_service(db)
        result = service.create(data)
        return Response.ok_data(result.model_dump(), _("ACCOUNT_CREATED"), 201, NAME)
    except ValueError as e:
        return Response.error(_("INVALID_DATA"), str(e), 400, NAME)
    except Exception as e:
        logger = setup_logger(NAME or "default_error_source")
        logger.exception("Unhandled error in create %s: %s", NAME, str(e))
        return Response.error(_("INTERNAL_ERROR"), _("UNEXPECTED_ERROR"), 500, NAME)


@router.get("/accounts/{id_account:int}")
def get_by_id(id_account: int, db: Session = Depends(get_db)):
    print("🔥 ENDPOINT GET_BY_ID HIT")
    print("🔥 ENDPOINT GET_BY_ID HIT")
    
    """Get a single account by ID."""
    try:
        service = _get_service(db)
        result = service.get_by_id(id_account)
        print("IBAN ORM:", result.iban)
        print("RAW ORM:", result)
        print("RAW IBAN:", result.iban)
        print("RAW __dict__:", result.__dict__)
        if not result:
            return Response.error(_("ACCOUNT_NOT_FOUND"), _("NONE"), 404, NAME)
          # 👇 DEBUG AQUÍ
        return Response.ok_data(result.model_dump(), _("ACCOUNT_FOUND"), 200, NAME)
    except Exception as e:
        logger = setup_logger(NAME or "default_error_source")
        logger.exception("Unhandled error in create %s: %s", NAME, str(e))
        return Response.error(_("INTERNAL_ERROR"), _("UNEXPECTED_ERROR"), 500, NAME)


@router.get("/accounts")
def list_all(db: Session = Depends(get_db)):
    """Get all accounts."""
    try:
        service = _get_service(db)
        results = service.get_all()

        return Response.ok_data(
            [r.model_dump() for r in results],
            _("ACCOUNT_LIST"),
            200,
            NAME
        )
    except Exception as e:
        logger = setup_logger(NAME or "default_error_source")
        logger.exception("Unhandled error in create %s: %s", NAME, str(e))
        return Response.error(_("INTERNAL_ERROR"), _("UNEXPECTED_ERROR"), 500, NAME)


@router.patch("/accounts/{id_account:int}")
def update(id_account: int, payload: AccountUpdate, db: Session = Depends(get_db)):
    """Update an account."""
    try:
        data = AccountUpdate.model_validate(payload)
    except ValidationError as e:
        return Response.error(_("VALIDATION_ERROR"), e.errors(), 400, NAME)

    try:
        service = _get_service(db)
        result = service.update(id_account, data)

        if not result:
            return Response.error(_("ACCOUNT_NOT_FOUND"), _("NONE"), 404, NAME)

        return Response.ok_data(result.model_dump(), _("ACCOUNT_UPDATED"), 200, NAME)
    except Exception as e:
        logger = setup_logger(NAME or "default_error_source")
        logger.exception("Unhandled error in create %s: %s", NAME, str(e))
        return Response.error(_("INTERNAL_ERROR"), _("UNEXPECTED_ERROR"), 500, NAME)


@router.delete("/accounts/{id_account:int}")
def delete(id_account: int, db: Session = Depends(get_db)):
    """Delete an account."""
    try:
        service = _get_service(db)
        success = service.delete(id_account)

        if not success:
            return Response.error(_("ACCOUNT_NOT_FOUND"), _("NONE"), 404, NAME)

        return Response.ok_message(_("ACCOUNT_DELETED"), 204, NAME)
    except Exception as e:
        logger = setup_logger(NAME or "default_error_source")
        logger.exception("Unhandled error in create %s: %s", NAME, str(e))
        return Response.error(_("INTERNAL_ERROR"), _("UNEXPECTED_ERROR"), 500, NAME)


@router.get("/meta/account")
def get_meta():
    return export_schema(AccountCreate)
