from flask import Blueprint, request, jsonify, abort
from sqlalchemy.orm import Session
from pydantic import ValidationError
from flask_babel import Babel, _


from models.models import IncomesCategory

from schemas.income_category_schema import IncomeCategoryRead, IncomeCategoryUpdate, IncomeCategoryCreate
from db.database import get_db
from services.response_service import Response


router = Blueprint("income_categories", __name__)
name="income_categories"
@router.post("/income_categories")
def create_expense_category():
    db = next(get_db())
    try:
        expense_category_data = IncomeCategoryCreate(**request.json)
    except ValidationError as e:
        return Response._error(_("INVALID_DATA"),e.errors(), 400, name)
    new_expense_category = IncomesCategory(**expense_category_data.model_dump())
    db.add(new_expense_category)
    db.commit()
    db.refresh(new_expense_category)
    return Response._ok_data(IncomeCategoryRead.model_validate(new_expense_category).model_dump(),_("INCOME_CATEGORY_CREATED"), 201, name)

@router.get("/income_categories/<int:expense_category_id>")
def get_expense_category(expense_category_id):
    db = next(get_db())
    expense_category = db.query(IncomesCategory).filter(IncomesCategory.id == expense_category_id).first()
    if not expense_category:
        return Response._error(_("INCOME_CATEGORY_NOT_FOUND"),_("NONE"), 404, name)
    return Response._ok_data(IncomeCategoryRead.model_validate(expense_category).model_dump(),_("INCOME_CATEGORY_FOUND"), 200, name)

@router.patch("/income_categories/<int:expense_category_id>")
def update_expense_category(expense_category_id):
    db = next(get_db())
    expense_category = db.query(IncomesCategory).filter(IncomesCategory.id == expense_category_id).first()
    if not expense_category:
        return Response._error(_("INCOME_CATEGORY_NOT_FOUND"), _("NONE"), 404, name)

    try:
        expense_category_data = IncomeCategoryUpdate(**request.json)
    except ValidationError as e:
        return Response._error(_("VALIDATION_ERROR"), e.errors(), 400, name)
        
    validated_data = expense_category_data.model_dump(exclude_unset=True)
    for key, value in validated_data.items():
        setattr(expense_category, key, value)

    db.commit()
    db.refresh(expense_category)
    return Response._ok_data(IncomeCategoryRead.model_validate(expense_category).model_dump(),_("INCOME_CATEGORY_UPDATED"), 200, name)

@router.get("/income_categories")
def list_income_categories():
    db = next(get_db())
    income_categories = db.query(IncomesCategory).all()
    # Convert SQLAlchemy models to Pydantic UserRead and serialize
    expense_category_data = [IncomeCategoryRead.model_validate(u).model_dump() for u in income_categories]
    if not expense_category_data:
        return Response._error(_("INCOME_CATEGORY_NOT_FOUND"),_("NONE"), 404, name)
    return Response._ok_data(expense_category_data,_("INCOME_CATEGORY_FOUND"), 200, name)
