from flask import Blueprint, request, jsonify, abort
from sqlalchemy.orm import Session
from pydantic import ValidationError
from flask_babel import _
from services.response_service import Response

from models.models import Investment
from schemas.investment_schema import InvestmentCreate, InvestmentRead, InvestmentUpdate
from db.database import get_db


router = Blueprint('investments', __name__)

@router.post("/investments")
def create_investment():
    db: Session = next(get_db())
    try:
        investment_data = InvestmentCreate.model_validate(request.json, context={"db": db})
    except ValidationError as e:
        return Response._error(_("FK_ERROR_ADD_DATA"),e.errors(), 400)
    new_investment = Investment(**investment_data.model_dump())
    db.add(new_investment)
    db.commit()
    db.refresh(new_investment)
    return jsonify(InvestmentRead.model_validate(new_investment).model_dump(), 201)

@router.get("/investments/<int:investment_id>")
def get_investment(investment_id):
    db: Session = next(get_db())
    investment = db.query(Investment).filter(Investment.id == investment_id).first()
    if not investment:
        return jsonify({"error": _("INVESTMENT_NOT_FOUND"), "details": _("None")}), 404
    return jsonify(InvestmentRead.model_validate(investment).model_dump())

@router.patch("/investments/<int:investment_id>")
def update_investment(investment_id):
    db: Session = next(get_db())
    investment = db.query(Investment).filter(Investment.id == investment_id).first()
    if not investment:
        return Response._error(_("INVESTMENT_NOT_FOUND"),_("None"), 404)

    try:
        investment_data = InvestmentUpdate(**request.json)
    except ValidationError as e:
        return Response._error(_("VALIDATION_ERROR"), e.errors(),400)

    validated_data = investment_data.model_dump(exclude_unset=True)
    for key, value in validated_data.items():
        setattr(investment, key, value)

    db.commit()
    db.refresh(investment)
    return jsonify(InvestmentRead.model_validate(investment).model_dump())

@router.delete("/investments/<int:investment_id>")
def delete_investment(investment_id):
    db: Session = next(get_db())
    investment = db.query(Investment).filter(Investment.id == investment_id).first()
    if not investment:
        return Response._error(("INVESTMENT_NOT_FOUND"),_("None"), 404)
    db.delete(investment)
    db.commit()
    return Response._error(_("INVESTMENT_DELETED"),_("NONE"), 204)

@router.get("/investments")
def list_investments():
    db: Session = next(get_db())
    investments = db.query(Investment).all()
    investment_data = [InvestmentRead.model_validate(u).model_dump() for u in investments]
    if not investment_data:
        return Response._error(_("INVESTMENT_NOT_FOUND"),_("None"), 404)
    return jsonify(investment_data)
