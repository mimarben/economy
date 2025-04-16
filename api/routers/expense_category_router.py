from flask import Blueprint, request, jsonify, abort
from sqlalchemy.orm import Session
from pydantic import ValidationError
from flask_babel import Babel, _


from models.models import ExpensesCategory

from schemas.expense_category_schema import ExpensesCategoryRead, ExpensesCategoryUpdate, ExpensesCategoryCreate
from db.database import get_db



router = Blueprint("expense_categories", __name__)

@router.post("/expense_categories")
def create_expense_category():
    db = next(get_db())
    try:
        expense_category_data = ExpensesCategoryCreate(**request.json)
    except ValidationError as e:
        return jsonify({"error": _("INVALID_DATA"), "details": e.errors()}), 400
    new_expense_category = ExpensesCategory(**expense_category_data.model_dump())
    db.add(new_expense_category)
    db.commit()
    db.refresh(new_expense_category)
    return jsonify(ExpensesCategoryRead.model_validate(new_expense_category).model_dump())

@router.get("/expense_categories/<int:expense_categories_id>")
def get_expense_category(expense_categories_id):
    db = next(get_db())
    expense_category = db.query(ExpensesCategory).filter(ExpensesCategory.id == expense_categories_id).first()
    if not expense_category:
        return jsonify({"error": _("EXPENSE_CATEGORY_NOT_FOUND"), "details": "None"}), 404
    return jsonify(ExpensesCategoryRead.model_validate(expense_category).model_dump())

@router.patch("/expense_categories/<int:expense_categories_id>")
def update_expense_category(expense_categories_id):
    db = next(get_db())
    expense_category = db.query(ExpensesCategory).filter(ExpensesCategory.id == expense_categories_id).first()
    if not expense_category:
        return jsonify({"error": _("EXPENSE_CATEGORY_NOT_FOUND"), "details": "None"}), 404

    try:
        expense_category_data = ExpensesCategoryUpdate(**request.json)
    except ValidationError as e:
        return jsonify({"error": _("VALIDATION_ERROR"), "details": e.errors()}), 400
        
    validated_data = expense_category_data.model_dump(exclude_unset=True)
    for key, value in validated_data.items():
        setattr(expense_category, key, value)


    db.commit()
    db.refresh(expense_category)
    return jsonify(ExpensesCategoryRead.model_validate(expense_category).model_dump())

@router.get("/expense_categories")
def list_expense_categories():
    db = next(get_db())
    expense_categories = db.query(ExpensesCategory).all()
    # Convert SQLAlchemy models to Pydantic UserRead and serialize
    expense_category_data = [ExpensesCategoryRead.model_validate(u).model_dump() for u in expense_categories]
    if not expense_category_data:
        return jsonify({"error": _("EXPENSE_CATEGORY_NOT_FOUND"), "details": "None"}), 404
    return jsonify(expense_category_data)
