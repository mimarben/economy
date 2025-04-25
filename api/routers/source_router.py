from flask import Blueprint, request, jsonify, abort
from sqlalchemy.orm import Session
from pydantic import ValidationError
from flask_babel import Babel, _


from models.models import Source

from schemas.source_schema import SourceCreate, SourceUpdate, SourceRead
from db.database import get_db
from services.response_service import Response


router = Blueprint("sources", __name__)
name="source_router"
@router.post("/sources")
def create_source():
    db = next(get_db())
    try:
        source_data = SourceCreate(**request.json)
    except ValidationError as e:
        return Response._error(_("INVALID_DATA"),e.errors(), 400, name)
    new_source = Source(**source_data.model_dump())
    db.add(new_source)
    db.commit()
    db.refresh(new_source)
    return Response._ok_data(SourceRead.model_validate(new_source).model_dump(),_("SOURCE_CREATED"), 201, name)

@router.get("/sources/<int:source_id>")
def get_source(source_id):
    db = next(get_db())
    source = db.query(Source).filter(Source.id == source_id).first()
    if not source:
        return Response._error(_("SOURCE_NOT_FOUND"),_("NONE"), 404, name)
    return Response._ok_data(SourceRead.model_validate(source).model_dump())

@router.patch("/sources/<int:source_id>")
def update_source(source_id):
    db = next(get_db())
    source = db.query(Source).filter(Source.id == source_id).first()
    if not source:
        return Response._error(_("SOURCE_NOT_FOUND"),_("NONE"), 404, name)

    try:
        source_data = SourceUpdate(**request.json)
    except ValidationError as e:
        return Response._error(_("VALIDATION_ERROR"),e.errors(), 400, name)        
    validated_data = source_data.model_dump(exclude_unset=True)
    for key, value in validated_data.items():
        setattr(source, key, value)


    db.commit()
    db.refresh(source)
    return Response._ok_data(SourceRead.model_validate(source).model_dump(),_("SOURCE_UPDATED"), 200, name)

@router.get("/sources")
def list_sources():
    db = next(get_db())
    sources = db.query(Source).all()
    # Convert SQLAlchemy models to Pydantic UserRead and serialize
    source_data = [SourceRead.model_validate(u).model_dump() for u in sources]
    if not source_data:
        return Response._error(_("SOURCE_NOT_FOUND"),_("NONE"), 404, name)
    return Response._ok_data(source_data,_("SOURCES_FOUND"), 200, name = name)
