from flask import Blueprint, request, jsonify, abort
from sqlalchemy.orm import Session
from pydantic import ValidationError
from flask_babel import Babel, _


from models.models import Bank

from schemas.bank_schema import BankCreate, BankUpdate, BankRead
from db.database import get_db



router = Blueprint("banks", __name__)

@router.post("/banks")
def create_bank():
    db = next(get_db())
    try:
        bank_data = BankCreate(**request.json)
    except ValidationError as e:
        return jsonify({"error": _("INVALID_DATA"), "details": e.errors()}), 400
    new_bank = Bank(**bank_data.model_dump())
    db.add(new_bank)
    db.commit()
    db.refresh(new_bank)
    return jsonify(BankRead.model_validate(new_bank).model_dump())

@router.get("/banks/<int:bank_id>")
def get_bank(bank_id):
    db = next(get_db())
    place = db.query(Bank).filter(Bank.id == bank_id).first()
    if not place:
        return jsonify({"error": _("BANK_NOT_FOUND"), "details": "None"}), 404
    return jsonify(BankRead.model_validate(place).model_dump())

@router.patch("/banks/<int:bank_id>")
def update_bank(bank_id):
    db = next(get_db())
    place = db.query(Bank).filter(Bank.id == bank_id).first()
    if not place:
        return jsonify({"error": _("BANK_NOT_FOUND"), "details": "None"}), 404

    try:
        bank_data = BankUpdate(**request.json)
    except ValidationError as e:
        return jsonify({"error": _("VALIDATION_ERROR"), "details": e.errors()}), 400
        
    validated_data = bank_data.model_dump(exclude_unset=True)
    for key, value in validated_data.items():
        setattr(place, key, value)


    db.commit()
    db.refresh(place)
    return jsonify(BankRead.model_validate(place).model_dump())

@router.get("/banks")
def list_banks():
    db = next(get_db())
    banks = db.query(Bank).all()
    # Convert SQLAlchemy models to Pydantic UserRead and serialize
    bank_data = [BankRead.model_validate(u).model_dump() for u in banks]
    if not bank_data:
        return jsonify({"error": _("BANK_NOT_FOUND"), "details": "None"}), 404
    return jsonify(bank_data)
