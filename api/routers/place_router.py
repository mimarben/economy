from flask import Blueprint, request, jsonify, abort
from sqlalchemy.orm import Session
from pydantic import ValidationError
from flask_babel import Babel, _


from models.models import Place

from schemas.place_schema import PlaceCreate, PlaceUpdate, PlaceRead
from db.database import get_db



router = Blueprint("places", __name__)

@router.post("/places")
def create_place():
    db = next(get_db())
    try:
        place_data = PlaceCreate(**request.json)
    except ValidationError as e:
        return jsonify({"error": _("INVALID_DATA"), "details": e.errors()}), 400
    new_place = Place(**place_data.model_dump())
    db.add(new_place)
    db.commit()
    db.refresh(new_place)
    return jsonify(PlaceRead.model_validate(new_place).model_dump())

@router.get("/places/<int:place_id>")
def get_place(place_id):
    db = next(get_db())
    place = db.query(Place).filter(Place.id == place_id).first()
    if not place:
        return jsonify({"error": _("PLACE_NOT_FOUND"), "details": "None"}), 404
    return jsonify(PlaceRead.model_validate(place).model_dump())

@router.patch("/places/<int:place_id>")
def update_place(place_id):
    db = next(get_db())
    place = db.query(Place).filter(Place.id == place_id).first()
    if not place:
        return jsonify({"error": _("PLACE_NOT_FOUND"), "details": "None"}), 404

    try:
        place_data = PlaceUpdate(**request.json)
    except ValidationError as e:
        return jsonify({"error": _("VALIDATION_ERROR"), "details": e.errors()}), 400
        
    validated_data = place_data.model_dump(exclude_unset=True)
    for key, value in validated_data.items():
        setattr(place, key, value)


    db.commit()
    db.refresh(place)
    return jsonify(PlaceRead.model_validate(place).model_dump())

@router.get("/places")
def list_places():
    db = next(get_db())
    places = db.query(Place).all()
    # Convert SQLAlchemy models to Pydantic UserRead and serialize
    place_data = [PlaceRead.model_validate(u).model_dump() for u in places]
    return jsonify(place_data)
