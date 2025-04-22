from flask import Blueprint, request, jsonify, abort
from sqlalchemy.orm import Session
from pydantic import ValidationError
from flask_babel import _
from services.response_service import Response

from models.models import Saving
from schemas.saving_schema import SavingCreate, SavingRead, SavingUpdate
from db.database import get_db


router = Blueprint('savings', __name__)

@router.post("/savings")
def create_saving():
    db: Session = next(get_db())
    try:
        saving_data = SavingCreate.model_validate(request.json, context={"db": db})
    except ValidationError as e:
        return Response._error(_("FK_ERROR_ADD_DATA"),e.errors(), 400)
    new_saving = Saving(**saving_data.model_dump())
    db.add(new_saving)
    db.commit()
    db.refresh(new_saving)
    return jsonify(SavingRead.model_validate(new_saving).model_dump(), 201)

@router.get("/savings/<int:saving_id>")
def get_saving(saving_id):
    db: Session = next(get_db())
    saving = db.query(Saving).filter(Saving.id == saving_id).first()
    if not saving:
        return jsonify({"error": _("SAVING_NOT_FOUND"), "details": _("None")}), 404
    return jsonify(SavingRead.model_validate(saving).model_dump())

@router.patch("/savings/<int:saving_id>")
def update_saving(saving_id):
    db: Session = next(get_db())
    saving = db.query(Saving).filter(Saving.id == saving_id).first()
    if not saving:
        return Response._error(_("SAVING_NOT_FOUND"),_("None"), 404)

    try:
        saving_data = SavingUpdate(**request.json)
    except ValidationError as e:
        return Response._error(_("VALIDATION_ERROR"), e.errors(),400)

    validated_data = saving_data.model_dump(exclude_unset=True)
    for key, value in validated_data.items():
        setattr(saving, key, value)

    db.commit()
    db.refresh(saving)
    return jsonify(SavingRead.model_validate(saving).model_dump())

@router.delete("/savings/<int:saving_id>")
def delete_saving(saving_id):
    db: Session = next(get_db())
    saving = db.query(Saving).filter(Saving.id == saving_id).first()
    if not saving:
        return Response._error(("SAVING_NOT_FOUND"),_("None"), 404)
    db.delete(saving)
    db.commit()
    return Response._error(_("SAVING_DELETED"),_("NONE"), 204)

@router.get("/savings")
def list_savings():
    db: Session = next(get_db())
    savings = db.query(Saving).all()
    saving_data = [SavingRead.model_validate(u).model_dump() for u in savings]
    if not saving_data:
        return Response._error(_("SAVING_NOT_FOUND"),_("None"), 404)
    return jsonify(saving_data)
