from flask import Blueprint, request, jsonify, abort
from sqlalchemy.orm import Session
from pydantic import ValidationError
from flask_babel import _
from services.response_service import Response

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
        return Response._error(_("FK_ERROR_ADD_DATA"),e.errors(), 400)
    new_expense = Expense(**expense_data.model_dump())
    db.add(new_expense)
    db.commit()
    db.refresh(new_expense)
    return jsonify(ExpenseRead.model_validate(new_expense).model_dump(), 201)

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
        return Response._error(_("EXPENSE_NOT_FOUND"),_("None"), 404)

    try:
        expense_data = ExpenseUpdate(**request.json)
    except ValidationError as e:
        return Response._error(_("VALIDATION_ERROR"), e.errors(),400)

    validated_data = expense_data.model_dump(exclude_unset=True)
    for key, value in validated_data.items():
        setattr(expense, key, value)

    db.commit()
    db.refresh(expense)
    return jsonify(ExpenseRead.model_validate(expense).model_dump())

@router.delete("/expenses/<int:expense_id>")
def delete_expense(expense_id):
    db: Session = next(get_db())
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        return Response._error(("EXPENSE_NOT_FOUND"),_("None"), 404)
    db.delete(expense)
    db.commit()
    return Response._error(_("EXPENSE_DELETED"),_("NONE"), 204)

@router.get("/expenses")
def list_expenses():
    db: Session = next(get_db())
    expenses = db.query(Expense).all()
    expense_data = [ExpenseRead.model_validate(u).model_dump() for u in expenses]
    if not expense_data:
        return Response._error(_("EXPENSE_NOT_FOUND"),_("None"), 404)
    return jsonify(expense_data)
