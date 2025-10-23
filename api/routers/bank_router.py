from flask import Blueprint, request, jsonify, abort
from sqlalchemy.orm import Session
from pydantic import ValidationError
from flask_babel import Babel, _


from models.models import Bank

from schemas.bank_schema import BankCreate, BankUpdate, BankRead
from db.database import get_db
from services.response_service import Response


router = Blueprint("banks", __name__)
name="banks"
@router.post("/banks")
def create_bank():
    db = next(get_db())
    try:
        bank_data = BankCreate(**request.json)
    except ValidationError as e:
        return Response._error(_("INVALID_DATA"), e.errors(), 400, name)
    new_bank = Bank(**bank_data.model_dump())
    db.add(new_bank)
    db.commit()
    db.refresh(new_bank)
    return Response._ok_data(BankRead.model_validate(new_bank).model_dump(), _("BANK_CREATED"), 201, name)

@router.get("/banks/<int:bank_id>")
def get_bank(bank_id):
    db = next(get_db())
    place = db.query(Bank).filter(Bank.id == bank_id).first()
    if not place:
        return Response._error(_("BANK_NOT_FOUND"),_("NONE"), 404, name)
    return Response._ok_data(BankRead.model_validate(place).model_dump(),_("BANK_FOUND"), 200, name) 

@router.patch("/banks/<int:bank_id>")
def update_bank(bank_id):
    db = next(get_db())
    place = db.query(Bank).filter(Bank.id == bank_id).first()
    if not place:
        return Response._error(_("BANK_NOT_FOUND"), _("NONE"), 404, name)

    try:
        bank_data = BankUpdate(**request.json)
    except ValidationError as e:
        return Response._error(_("VALIDATION_ERROR"), e.errors(), 400, name)
        
    validated_data = bank_data.model_dump(exclude_unset=True)
    for key, value in validated_data.items():
        setattr(place, key, value)
    db.commit()
    db.refresh(place)
    return Response._ok_data(BankRead.model_validate(place).model_dump(), _("BANK_UPDATED"), 200, name)

@router.get("/banks")
def list_banks():
    db = next(get_db())
    banks = db.query(Bank).all()
    # Convert SQLAlchemy models to Pydantic UserRead and serialize
    bank_data = [BankRead.model_validate(u).model_dump() for u in banks]
    if not bank_data:
        return Response._error(_("BANK_NOT_FOUND"),_("NONE"), 404, name)
    return Response._ok_data(bank_data, _("BANKS_FOUND"), 200, name)
