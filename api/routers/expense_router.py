from flask import Blueprint, request, jsonify, abort
from sqlalchemy.orm import Session
from pydantic import ValidationError
from flask_babel import _
from services.response import Response

from models.models import Expense, User, Place, ExpensesCategory
from schemas.expense_schema import ExpenseCreate, ExpenseRead, ExpenseUpdate
from db.database import get_db


router = Blueprint('expenses', __name__)

@router.post("/expenses")
def create_expense():
    db: Session = next(get_db())
    try:
        expense_data = ExpenseCreate.model_validate(request.json, context={"db": db})
    except ValidationError as e:
        return jsonify({
        "error": "INVALID_DATA",
        "details": e.errors()  # will now contain your custom error messages!
    }), 400

    new_expense = Expense(**expense_data.model_dump())
    db.add(new_expense)
    db.commit()
    db.refresh(new_expense)
    return Response._ok(ExpenseRead(new_expense).model_dump(), 201)

@router.get("/expenses/<int:expense_id>")
def get_expense(expense_id):
    db: Session = next(get_db())
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        return jsonify({"error": _("EXPENSE_NOT_FOUND"), "details": _("None")}), 404
    return jsonify(ExpenseRead.model_validate(expense).model_dump())

@router.patch("/expenses/<int:expense_id>")
def update_expense(expense_id):
    db: Session = next(get_db())
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        return jsonify({"error": _("EXPENSE_NOT_FOUND"), "details": _("None")}), 404

    try:
        expense_data = ExpenseUpdate(**request.json)
    except ValidationError as e:
        return jsonify({"error": _("VALIDATION_ERROR"), "details": e.errors()}), 400

    validated_data = expense_data.model_dump(exclude_unset=True)
    for key, value in validated_data.items():
        setattr(expense, key, value)

    db.commit()
    db.refresh(expense)
    return jsonify(ExpenseRead.from_attributes(expense).dict())

@router.delete("/expenses/<int:expense_id>")
def delete_expense(expense_id):
    db: Session = next(get_db())
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        return jsonify({"error": _("EXPENSE_NOT_FOUND"), "details": _("None")}), 404

    db.delete(expense)
    db.commit()
    return jsonify({"message": "EXPENSE_DELETED"}), 204

@router.get("/expenses")
def list_expenses():
    db: Session = next(get_db())
    expenses = db.query(Expense).all()
    expense_data = [ExpenseRead.model_validate(u).model_dump() for u in expenses]
    if not expense_data:
        return jsonify({"error": _("EXPENSE_NOT_FOUND"), "details": _("None")}), 404
    return jsonify(expense_data)
