from flask import Blueprint, request, jsonify, abort
from sqlalchemy.orm import Session
from pydantic import ValidationError
from flask_babel import _

from models.models import Income
from schemas.income_schema import IncomeCreate, IncomeRead, IncomeUpdate
from db.database import get_db
from services.response_service import Response


router = Blueprint('incomes', __name__)
name="incomes"
@router.post("/incomes")
def create_income():
    db: Session = next(get_db())
    try:
        income_data = IncomeCreate.model_validate(request.json, context={"db": db})
    except ValidationError as e:
        return Response._error(_("FK_ERROR_ADD_DATA"),e.errors(), 400, name)
    new_income = Income(**income_data.model_dump())
    db.add(new_income)
    db.commit()
    db.refresh(new_income)
    return Response._ok_data(IncomeRead.model_validate(new_income).model_dump(),_("INCOME_CREATED") ,201, name)

@router.get("/incomes/<int:income_id>")
def get_income(income_id):
    db: Session = next(get_db())
    income = db.query(Income).filter(Income.id == income_id).first()
    if not income:
        return Response._error(_("INCOME_NOT_FOUND"), _("NONE"), 404, name)
    return Response._ok_data(IncomeRead.model_validate(income).model_dump(),_("INCOME_FOUND"), 200, name)

@router.patch("/incomes/<int:income_id>")
def update_income(income_id):
    db: Session = next(get_db())
    income = db.query(Income).filter(Income.id == income_id).first()
    if not income:
        return Response._error(_("INCOME_NOT_FOUND"),_("NONE"), 404, name)

    try:
        income_data = IncomeUpdate(**request.json)
    except ValidationError as e:
        return Response._error(_("VALIDATION_ERROR"), e.errors(),400, name)

    validated_data = income_data.model_dump(exclude_unset=True)
    for key, value in validated_data.items():
        setattr(income, key, value)

    db.commit()
    db.refresh(income)
    return Response._ok_data(IncomeRead.model_validate(income).model_dump(),_("INCOME_UPDATED"), 200, name)

@router.delete("/incomes/<int:income_id>")
def delete_income(income_id):
    db: Session = next(get_db())
    income = db.query(Income).filter(Income.id == income_id).first()
    if not income:
        return Response._error(("INCOME_NOT_FOUND"),_("NONE"), 404, name)
    db.delete(income)
    db.commit()
    return Response._error(_("INCOME_DELETED"),_("NONE"), 204, name)

@router.get("/incomes")
def list_incomes():
    db: Session = next(get_db())
    incomes = db.query(Income).all()
    income_data = [IncomeRead.model_validate(u).model_dump() for u in incomes]
    if not income_data:
        return Response._error(_("INCOME_NOT_FOUND"),_("NONE"), 404, name)
    return Response._ok_data(income_data, _("INCOME_FOUND"), 200, name)
