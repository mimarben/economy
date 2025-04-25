from flask import Blueprint, request, jsonify, abort
from sqlalchemy.orm import Session
from pydantic import ValidationError
from flask_babel import Babel, _


from models.models import Place

from schemas.place_schema import PlaceCreate, PlaceUpdate, PlaceRead
from db.database import get_db
from services.response_service import Response



router = Blueprint("places", __name__)
name= "places"
@router.post("/places")
def create_place():
    db = next(get_db())
    try:
        place_data = PlaceCreate(**request.json)
    except ValidationError as e:
        return Response._error(_("INVALID_DATA"),e.errors(), 400, name)
    new_place = Place(**place_data.model_dump())
    db.add(new_place)
    db.commit()
    db.refresh(new_place)
    return Response._ok_data(PlaceRead.model_validate(new_place).model_dump(),_("PLACE_CREATED"),201, name)

@router.get("/places/<int:place_id>")
def get_place(place_id):
    db = next(get_db())
    place = db.query(Place).filter(Place.id == place_id).first()
    if not place:
        return Response._error(_("PLACE_NOT_FOUND"), _("NONE"), 404, name)
    return Response._ok_data(PlaceRead.model_validate(place).model_dump(),_("PLACE_FOUND"),200, name)

@router.patch("/places/<int:place_id>")
def update_place(place_id):
    db = next(get_db())
    place = db.query(Place).filter(Place.id == place_id).first()
    if not place:
        return Response._error(_("PLACE_NOT_FOUND"),_("NONE"), 404, name)

    try:
        place_data = PlaceUpdate(**request.json)
    except ValidationError as e:
        return Response._error(_("VALIDATION_ERROR"),e.errors(), 400, name)
        
    validated_data = place_data.model_dump(exclude_unset=True)
    for key, value in validated_data.items():
        setattr(place, key, value)


    db.commit()
    db.refresh(place)
    return Response._ok_data(PlaceRead.model_validate(place).model_dump(),_("PLACE_UPDATED"), 201, name)

@router.get("/places")
def list_places():
    db = next(get_db())
    places = db.query(Place).all()
    # Convert SQLAlchemy models to Pydantic UserRead and serialize
    place_data = [PlaceRead.model_validate(u).model_dump() for u in places]
    if not place_data:
        return Response._error(_("PLACE_NOT_FOUND"), _("NONE"), 404, name)
    return Response._ok_data(place_data, _("PLACE_FOUND"), 200, name)
