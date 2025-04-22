from flask import Blueprint, request, jsonify, abort
from sqlalchemy.orm import Session
from pydantic import ValidationError
from flask_babel import Babel, _


from models.models import Source

from schemas.source_schema import SourceCreate, SourceUpdate, SourceRead
from db.database import get_db



router = Blueprint("sources", __name__)

@router.post("/sources")
def create_source():
    db = next(get_db())
    try:
        source_data = SourceCreate(**request.json)
    except ValidationError as e:
        return jsonify({"error": _("INVALID_DATA"), "details": e.errors()}), 400
    new_source = Source(**source_data.model_dump())
    db.add(new_source)
    db.commit()
    db.refresh(new_source)
    return jsonify(SourceRead.model_validate(new_source).model_dump())

@router.get("/sources/<int:source_id>")
def get_source(source_id):
    db = next(get_db())
    source = db.query(Source).filter(Source.id == source_id).first()
    if not source:
        return jsonify({"error": _("SOURCE_NOT_FOUND"), "details": "None"}), 404
    return jsonify(SourceRead.model_validate(source).model_dump())

@router.patch("/sources/<int:source_id>")
def update_source(source_id):
    db = next(get_db())
    source = db.query(Source).filter(Source.id == source_id).first()
    if not source:
        return jsonify({"error": _("SOURCE_NOT_FOUND"), "details": "None"}), 404

    try:
        source_data = SourceUpdate(**request.json)
    except ValidationError as e:
        return jsonify({"error": _("VALIDATION_ERROR"), "details": e.errors()}), 400
        
    validated_data = source_data.model_dump(exclude_unset=True)
    for key, value in validated_data.items():
        setattr(source, key, value)


    db.commit()
    db.refresh(source)
    return jsonify(SourceRead.model_validate(source).model_dump())

@router.get("/sources")
def list_sources():
    db = next(get_db())
    sources = db.query(Source).all()
    # Convert SQLAlchemy models to Pydantic UserRead and serialize
    source_data = [SourceRead.model_validate(u).model_dump() for u in sources]
    if not source_data:
        return jsonify({"error": _("SOURCE_NOT_FOUND"), "details": "None"}), 404
    return jsonify(source_data)
