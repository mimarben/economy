from flask import Blueprint, request, jsonify, abort
from sqlalchemy.orm import Session
from pydantic import ValidationError
from flask_babel import Babel, _


from models.models import ExpensesCategory

from schemas.expense_category_schema import ExpenseCategoryRead, ExpenseCategoryUpdate, ExpenseCategoryCreate
from db.database import get_db



router = Blueprint("expenses_categories", __name__)

@router.post("/expenses_categories")
def create_expense_category():
    db = next(get_db())
    try:
        expense_category_data = ExpenseCategoryCreate(**request.json)
    except ValidationError as e:
        return jsonify({"error": _("INVALID_DATA"), "details": e.errors()}), 400
    new_expense_category = ExpensesCategory(**expense_category_data.model_dump())
    db.add(new_expense_category)
    db.commit()
    db.refresh(new_expense_category)
    return jsonify(ExpenseCategoryRead.model_validate(new_expense_category).model_dump())

@router.get("/expenses_categories/<int:expenses_categories_id>")
def get_expense_category(expenses_categories_id):
    db = next(get_db())
    expense_category = db.query(ExpensesCategory).filter(ExpensesCategory.id == expenses_categories_id).first()
    if not expense_category:
        return jsonify({"error": _("EXPENSE_CATEGORY_NOT_FOUND"), "details": "None"}), 404
    return jsonify(ExpenseCategoryRead.model_validate(expense_category).model_dump())

@router.patch("/expenses_categories/<int:expenses_categories_id>")
def update_expense_category(expenses_categories_id):
    db = next(get_db())
    expense_category = db.query(ExpensesCategory).filter(ExpensesCategory.id == expenses_categories_id).first()
    if not expense_category:
        return jsonify({"error": _("EXPENSE_CATEGORY_NOT_FOUND"), "details": "None"}), 404

    try:
        expense_category_data = ExpenseCategoryUpdate(**request.json)
    except ValidationError as e:
        return jsonify({"error": _("VALIDATION_ERROR"), "details": e.errors()}), 400
        
    validated_data = expense_category_data.model_dump(exclude_unset=True)
    for key, value in validated_data.items():
        setattr(expense_category, key, value)


    db.commit()
    db.refresh(expense_category)
    return jsonify(ExpenseCategoryRead.model_validate(expense_category).model_dump())

@router.get("/expenses_categories")
def list_expenses_categories():
    db = next(get_db())
    expenses_categories = db.query(ExpensesCategory).all()
    # Convert SQLAlchemy models to Pydantic UserRead and serialize
    expense_category_data = [ExpenseCategoryRead.model_validate(u).model_dump() for u in expenses_categories]
    if not expense_category_data:
        return jsonify({"error": _("EXPENSE_CATEGORY_NOT_FOUND"), "details": "None"}), 404
    return jsonify(expense_category_data)
