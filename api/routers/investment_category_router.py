from flask import Blueprint, request, jsonify, abort
from sqlalchemy.orm import Session
from pydantic import ValidationError
from flask_babel import Babel, _


from models.models import InvestmentsCategory

from schemas.investment_category_schema import InvestmentCategoryRead, InvestmentCategoryUpdate, InvestmentCategoryCreate
from db.database import get_db



router = Blueprint("investments_categories", __name__)

@router.post("/investments_categories")
def create_investment_category():
    db = next(get_db())
    try:
        investment_category_data = InvestmentCategoryCreate(**request.json)
    except ValidationError as e:
        return jsonify({"error": _("INVALID_DATA"), "details": e.errors()}), 400
    new_investment_category = InvestmentsCategory(**investment_category_data.model_dump())
    db.add(new_investment_category)
    db.commit()
    db.refresh(new_investment_category)
    return jsonify(InvestmentCategoryRead.model_validate(new_investment_category).model_dump())

@router.get("/investments_categories/<int:investment_category_id>")
def get_investment_category(investment_category_id):
    db = next(get_db())
    investment_category = db.query(InvestmentsCategory).filter(InvestmentsCategory.id == investment_category_id).first()
    if not investment_category:
        return jsonify({"error": _("INVESTMENT_CATEGORY_NOT_FOUND"), "details": "None"}), 404
    return jsonify(InvestmentCategoryRead.model_validate(investment_category).model_dump())

@router.patch("/investments_categories/<int:investment_category_id>")
def update_investment_category(investment_category_id):
    db = next(get_db())
    investment_category = db.query(InvestmentsCategory).filter(InvestmentsCategory.id == investment_category_id).first()
    if not investment_category:
        return jsonify({"error": _("INVESTMENT_CATEGORY_NOT_FOUND"), "details": "None"}), 404

    try:
        investment_category_data = InvestmentCategoryUpdate(**request.json)
    except ValidationError as e:
        return jsonify({"error": _("VALIDATION_ERROR"), "details": e.errors()}), 400
        
    validated_data = investment_category_data.model_dump(exclude_unset=True)
    for key, value in validated_data.items():
        setattr(investment_category, key, value)


    db.commit()
    db.refresh(investment_category)
    return jsonify(InvestmentCategoryRead.model_validate(investment_category).model_dump())

@router.get("/investments_categories")
def list_investments_categories():
    db = next(get_db())
    investments_categories = db.query(InvestmentsCategory).all()
    # Convert SQLAlchemy models to Pydantic UserRead and serialize
    investment_category_data = [InvestmentCategoryRead.model_validate(u).model_dump() for u in investments_categories]
    if not investment_category_data:
        return jsonify({"error": _("INVESTMENT_CATEGORY_NOT_FOUND"), "details": "None"}), 404
    return jsonify(investment_category_data)
