from flask import Blueprint, request, jsonify, abort
from sqlalchemy.orm import Session
from pydantic import ValidationError
from flask_babel import Babel, _


from api.models.models import Place

from api.schemas.place_schema import PlaceCreate, PlaceUpdate, PlaceRead
from api.db.database import get_db



router = Blueprint("places", __name__)
# Create a new place
@router.get("/places")
def list_places():
    db = next(get_db())
    places = db.query(Place).all()
    # Convert SQLAlchemy models to Pydantic UserRead and serialize
    place_data = [PlaceRead.model_validate(u).model_dump() for u in places]
    return jsonify(place_data)
