from flask import Blueprint, request, jsonify, abort
from sqlalchemy.orm import Session
from pydantic import ValidationError
from flask_babel import Babel, _


from models.models import Expense

from schemas.expense_schema import ExpenseCreate, ExpenseUpdate, ExpenseRead
from db.database import get_db



router = Blueprint("expenses", __name__)

@router.post("/expenses")
def create_place():
    db = next(get_db())
    try:
        expense_data = ExpenseCreate(**request.json)
    except ValidationError as e:
        return jsonify({"error": _("INVALID_DATA"), "details": e.errors()}), 400
    new_place = Expense(**expense_data.model_dump())
    db.add(new_place)
    db.commit()
    db.refresh(new_place)
    return jsonify(ExpenseRead.model_validate(new_place).model_dump())

@router.get("/expenses/<int:expense_id>")
def get_place(expense_id):
    db = next(get_db())
    place = db.query(Expense).filter(Expense.id == expense_id).first()
    if not place:
        return jsonify({"error": _("EXPENSE_NOT_FOUND"), "details": "None"}), 404
    return jsonify(ExpenseRead.model_validate(place).model_dump())

@router.patch("/expenses/<int:expense_id>")
def update_place(expense_id):
    db = next(get_db())
    place = db.query(Expense).filter(Expense.id == expense_id).first()
    if not place:
        return jsonify({"error": _("EXPENSE_NOT_FOUND"), "details": "None"}), 404

    try:
        expense_data = ExpenseUpdate(**request.json)
    except ValidationError as e:
        return jsonify({"error": _("VALIDATION_ERROR"), "details": e.errors()}), 400
        
    validated_data = expense_data.model_dump(exclude_unset=True)
    for key, value in validated_data.items():
        setattr(place, key, value)


    db.commit()
    db.refresh(place)
    return jsonify(ExpenseRead.model_validate(place).model_dump())

@router.get("/expenses")
def list_expenses():
    db = next(get_db())
    expenses = db.query(Expense).all()
    # Convert SQLAlchemy models to Pydantic UserRead and serialize
    expense_data = [ExpenseRead.model_validate(u).model_dump() for u in expenses]
    if not expense_data:
        return jsonify({"error": _("EXPENSE_NOT_FOUND"), "details": "None"}), 404
    return jsonify(expense_data)
