from flask import Blueprint, request, jsonify, abort
from sqlalchemy.orm import Session
from pydantic import ValidationError
from flask_babel import Babel, _


from models.models import HouseholdMember

from schemas.household_member_schema import HouseholdMemberCreate, HouseholdMemberUpdate, HouseholdMemberRead
from db.database import get_db



router = Blueprint("households_members", __name__)

@router.post("/households_members")
def create_household_member():
    db = next(get_db())
    try:
        household_member_data = HouseholdMemberCreate(**request.json)
    except ValidationError as e:
        return jsonify({"error": _("INVALID_DATA"), "details": e.errors()}), 400
    new_household_member = HouseholdMember(**household_member_data.model_dump())
    db.add(new_household_member)
    db.commit()
    db.refresh(new_household_member)
    return jsonify(HouseholdMemberRead.model_validate(new_household_member).model_dump())

@router.get("/households_members/<int:household_member_id>")
def get_household_member(household_member_id):
    db = next(get_db())
    household_member = db.query(HouseholdMember).filter(HouseholdMember.id == household_member_id).first()
    if not household_member:
        return jsonify({"error": _("MEMBER_NOT_FOUND"), "details": "None"}), 404
    return jsonify(HouseholdMemberRead.model_validate(household_member).model_dump())

@router.patch("/households_members/<int:household_member_id>")
def update_household_member(household_member_id):
    db = next(get_db())
    household_member = db.query(HouseholdMember).filter(HouseholdMember.id == household_member_id).first()
    if not household_member:
        return jsonify({"error": _("MEMBER_NOT_FOUND"), "details": "None"}), 404

    try:
        household_member_data = HouseholdMemberUpdate(**request.json)
    except ValidationError as e:
        return jsonify({"error": _("VALIDATION_ERROR"), "details": e.errors()}), 400
        
    validated_data = household_member_data.model_dump(exclude_unset=True)
    for key, value in validated_data.items():
        setattr(household_member, key, value)

    db.commit()
    db.refresh(household_member)
    return jsonify(HouseholdMemberRead.model_validate(household_member).model_dump())

@router.get("/households_members")
def list_households_members():
    db = next(get_db())
    households_members = db.query(HouseholdMember).all()
    # Convert SQLAlchemy models to Pydantic UserRead and serialize
    household_member_data = [HouseholdMemberRead.model_validate(u).model_dump() for u in households_members]
    if not household_member_data:
        return jsonify({"error": _("MEMBER_NOT_FOUND"), "details": "None"}), 404
    return jsonify(household_member_data)
