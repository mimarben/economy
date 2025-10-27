from flask import Blueprint, request, jsonify, abort
from sqlalchemy.orm import Session
from pydantic import ValidationError
from flask_babel import Babel, _
from models.models import Account
from schemas.account_schema import AccountCreate, AccountUpdate, AccountRead
from db.database import get_db
from services.response_service import Response


router = Blueprint("accounts", __name__)
name="accounts"
@router.post("/accounts")
def create_account():
    db = next(get_db())
    try:
        account_data = AccountCreate(**request.json)
    except ValidationError as e:
        return Response._error(_("INVALID_DATA"),e.errors(), 400, name)
    new_account = Account(**account_data.model_dump())
    db.add(new_account)
    db.commit()
    db.refresh(new_account)
    return Response._ok_data(AccountRead.model_validate(new_account).model_dump(),_("ACCOUNT_CREATED"), 201, name)

@router.get("/accounts/<int:account_id>")
def get_account(account_id):
    db = next(get_db())
    place = db.query(Account).filter(Account.id == account_id).first()
    if not place:
        return Response._error(_("ACCOUNT_NOT_FOUND"),_("NONE"), 404, name)
    return Response._ok_data(AccountRead.model_validate(place).model_dump(),_("ACCOUNT_FOUND"), 200, name)

@router.patch("/accounts/<int:account_id>")
def update_account(account_id):
    db = next(get_db())
    place = db.query(Account).filter(Account.id == account_id).first()
    if not place:
        return Response._error(_("ACCOUNT_NOT_FOUND"), _("NONE"), 404, name)

    try:
        account_data = AccountUpdate(**request.json)
    except ValidationError as e:
        return Response._error(_("VALIDATION_ERROR"),e.errors(), 400, name)

    validated_data = account_data.model_dump(exclude_unset=True)
    for key, value in validated_data.items():
        setattr(place, key, value)


    db.commit()
    db.refresh(place)
    return Response._ok_data(AccountRead.model_validate(place).model_dump(),_("ACCOUNT_UPDATED"), 200, name)

@router.get("/accounts")
def list_accounts():
    db = next(get_db())
    accounts = db.query(Account).all()
    # Convert SQLAlchemy models to Pydantic UserRead and serialize
    account_data = [AccountRead.model_validate(u).model_dump() for u in accounts]
    if not account_data:
        return Response._error(_("ACCOUNT_NOT_FOUND"),_("NONE"), 404, name)
    return Response._ok_data(account_data,_("ACCOUNT_FOUND"), 200, name)
