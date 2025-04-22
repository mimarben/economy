from flask import Blueprint, request, jsonify, abort
from sqlalchemy.orm import Session
from pydantic import ValidationError
from flask_babel import Babel, _


from models.models import IncomesCategory

from schemas.income_category_schema import IncomeCategoryRead, IncomeCategoryUpdate, IncomeCategoryCreate
from db.database import get_db



router = Blueprint("income_categories", __name__)

@router.post("/income_categories")
def create_expense_category():
    db = next(get_db())
    try:
        expense_category_data = IncomeCategoryCreate(**request.json)
    except ValidationError as e:
        return jsonify({"error": _("INVALID_DATA"), "details": e.errors()}), 400
    new_expense_category = IncomesCategory(**expense_category_data.model_dump())
    db.add(new_expense_category)
    db.commit()
    db.refresh(new_expense_category)
    return jsonify(IncomeCategoryRead.model_validate(new_expense_category).model_dump())

@router.get("/income_categories/<int:expense_category_id>")
def get_expense_category(expense_category_id):
    db = next(get_db())
    expense_category = db.query(IncomesCategory).filter(IncomesCategory.id == expense_category_id).first()
    if not expense_category:
        return jsonify({"error": _("INCOME_CATEGORY_NOT_FOUND"), "details": "None"}), 404
    return jsonify(IncomeCategoryRead.model_validate(expense_category).model_dump())

@router.patch("/income_categories/<int:expense_category_id>")
def update_expense_category(expense_category_id):
    db = next(get_db())
    expense_category = db.query(IncomesCategory).filter(IncomesCategory.id == expense_category_id).first()
    if not expense_category:
        return jsonify({"error": _("INCOME_CATEGORY_NOT_FOUND"), "details": "None"}), 404

    try:
        expense_category_data = IncomeCategoryUpdate(**request.json)
    except ValidationError as e:
        return jsonify({"error": _("VALIDATION_ERROR"), "details": e.errors()}), 400
        
    validated_data = expense_category_data.model_dump(exclude_unset=True)
    for key, value in validated_data.items():
        setattr(expense_category, key, value)

    db.commit()
    db.refresh(expense_category)
    return jsonify(IncomeCategoryRead.model_validate(expense_category).model_dump())

@router.get("/income_categories")
def list_income_categories():
    db = next(get_db())
    income_categories = db.query(IncomesCategory).all()
    # Convert SQLAlchemy models to Pydantic UserRead and serialize
    expense_category_data = [IncomeCategoryRead.model_validate(u).model_dump() for u in income_categories]
    if not expense_category_data:
        return jsonify({"error": _("INCOME_CATEGORY_NOT_FOUND"), "details": "None"}), 404
    return jsonify(expense_category_data)
