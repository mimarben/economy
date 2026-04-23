"""Router for Account endpoints following ISP - Dependency Inversion Principle."""
from flask import Blueprint, request
from sqlalchemy.orm import Session
from pydantic import ValidationError
from flask_babel import _

from models.finance.account_model import Account
from schemas.finance.account_schema import AccountBase, AccountCreate, AccountUpdate

from schemas.core.export_schema import export_schema

from services.finance.account_service import AccountService
from services.core.response_service import Response
from services.core.interfaces import IReadService, ICreateService, IUpdateService, IDeleteService
from services.logs.logger_service import setup_logger

from db.database import get_db


router = Blueprint("accounts", __name__)
NAME = "accounts"


# Dependency Injection - Each endpoint depends only on what it needs (ISP)
def _get_create_service(db: Session) -> ICreateService:
    """Inject only create interface."""
    return AccountService(db)


def _get_read_service(db: Session) -> IReadService:
    """Inject only read interface."""
    return AccountService(db)


def _get_update_service(db: Session) -> IUpdateService:
    """Inject only update interface."""
    return AccountService(db)


def _get_delete_service(db: Session) -> IDeleteService:
    """Inject only delete interface."""
    return AccountService(db)


@router.post("/accounts")
def create():
    """Create a new account."""
    db: Session = next(get_db())

    try:
        data = AccountCreate.model_validate(request.json)
    except ValidationError as e:
        return Response.error(_("VALIDATION_ERROR"), e.errors(), 400, NAME)

    try:
        service: ICreateService = _get_create_service(db)
        result = service.create(data)
        return Response.ok_data(result.model_dump(), _("ACCOUNT_CREATED"), 201, NAME)
    except ValueError as e:
        return Response.error(_("INVALID_DATA"), str(e), 400, NAME)
    except Exception as e:
        logger = setup_logger(NAME or "default_error_source")
        logger.exception("Unhandled error in create %s: %s", NAME, str(e))
        return Response.error(_("INTERNAL_ERROR"), _("UNEXPECTED_ERROR"), 500, NAME)


@router.get("/accounts/<int:id_account>")
def get_by_id(id_account):
    print("🔥 ENDPOINT GET_BY_ID HIT")
    print("🔥 ENDPOINT GET_BY_ID HIT")
    
    """Get a single account by ID."""
    db: Session = next(get_db())
    try:
        service: IReadService = _get_read_service(db)
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
def list_all():
    """Get all accounts."""
    db: Session = next(get_db())

    try:
        service: IReadService = _get_read_service(db)
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


@router.patch("/accounts/<int:id_account>")
def update(id_account):
    """Update an account."""
    db: Session = next(get_db())

    try:
        data = AccountUpdate.model_validate(request.json)
    except ValidationError as e:
        return Response.error(_("VALIDATION_ERROR"), e.errors(), 400, NAME)

    try:
        service: IUpdateService = _get_update_service(db)
        result = service.update(id_account, data)

        if not result:
            return Response.error(_("ACCOUNT_NOT_FOUND"), _("NONE"), 404, NAME)

        return Response.ok_data(result.model_dump(), _("ACCOUNT_UPDATED"), 200, NAME)
    except Exception as e:
        logger = setup_logger(NAME or "default_error_source")
        logger.exception("Unhandled error in create %s: %s", NAME, str(e))
        return Response.error(_("INTERNAL_ERROR"), _("UNEXPECTED_ERROR"), 500, NAME)


@router.delete("/accounts/<int:id_account>")
def delete(id_account):
    """Delete an account."""
    db: Session = next(get_db())

    try:
        service: IDeleteService = _get_delete_service(db)
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
