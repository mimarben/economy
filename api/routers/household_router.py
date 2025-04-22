from flask import Blueprint, request, jsonify, abort
from sqlalchemy.orm import Session
from pydantic import ValidationError
from flask_babel import Babel, _


from models.models import Household

from schemas.household_schema import HouseholdCreate, HouseholdUpdate, HouseholdRead
from db.database import get_db



router = Blueprint("households", __name__)

@router.post("/households")
def create_household():
    db = next(get_db())
    try:
        place_data = HouseholdCreate(**request.json)
    except ValidationError as e:
        return jsonify({"error": _("INVALID_DATA"), "details": e.errors()}), 400
    new_household = Household(**place_data.model_dump())
    db.add(new_household)
    db.commit()
    db.refresh(new_household)
    return jsonify(HouseholdRead.model_validate(new_household).model_dump())

@router.get("/households/<int:household_id>")
def get_household(household_id):
    db = next(get_db())
    place = db.query(Household).filter(Household.id == household_id).first()
    if not place:
        return jsonify({"error": _("HOUSEHOLD_NOT_FOUND"), "details": "None"}), 404
    return jsonify(HouseholdRead.model_validate(place).model_dump())

@router.patch("/households/<int:household_id>")
def update_household(household_id):
    db = next(get_db())
    place = db.query(Household).filter(Household.id == household_id).first()
    if not place:
        return jsonify({"error": _("HOUSEHOLD_NOT_FOUND"), "details": "None"}), 404

    try:
        place_data = HouseholdUpdate(**request.json)
    except ValidationError as e:
        return jsonify({"error": _("VALIDATION_ERROR"), "details": e.errors()}), 400
        
    validated_data = place_data.model_dump(exclude_unset=True)
    for key, value in validated_data.items():
        setattr(place, key, value)


    db.commit()
    db.refresh(place)
    return jsonify(HouseholdRead.model_validate(place).model_dump())

@router.get("/households")
def list_households():
    db = next(get_db())
    households = db.query(Household).all()
    # Convert SQLAlchemy models to Pydantic UserRead and serialize
    place_data = [HouseholdRead.model_validate(u).model_dump() for u in households]
    if not place_data:
        return jsonify({"error": _("HOUSEHOLD_NOT_FOUND"), "details": "None"}), 404
    return jsonify(place_data)
