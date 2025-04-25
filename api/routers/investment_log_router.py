from flask import Blueprint, request, jsonify, abort
from sqlalchemy.orm import Session
from pydantic import ValidationError
from flask_babel import _
from services.response_service import Response

from models.models import InvestmentLog
from schemas.investment_log_schema import InvestmentLogCreate, InvestmentLogRead, InvestmentLogUpdate
from db.database import get_db

router = Blueprint('investments_logs', __name__)

@router.post("/investments_logs")
def create_new_investment():
    db: Session = next(get_db())
    try:
        new_investment_data = InvestmentLogCreate.model_validate(request.json, context={"db": db})
    except ValidationError as e:
        return Response._error(_("FK_ERROR_ADD_DATA"),e.errors(), 400)
    new_investment_log = InvestmentLog(**new_investment_data.model_dump())
    db.add(new_investment_log)
    db.commit()
    db.refresh(new_investment_log)
    return Response._ok_data(InvestmentLogRead.model_validate(new_investment_log).model_dump(),_("QUERY_OK"), 201)

@router.get("/investments_logs/<int:investment_log_id>")
def get_new_investment(investment_log_id):
    db: Session = next(get_db())
    investment_log = db.query(InvestmentLog).filter(InvestmentLog.id == investment_log_id).first()
    if not investment_log:
        return Response._error(_("SAVING_NOT_FOUND"), _("SAVING_NOT_FOUND_NOT_EXIST"), 404)
    return Response._ok_data(InvestmentLogRead.model_validate(investment_log).model_dump(), _("QUERY_OK"), 200)

@router.patch("/investments_logs/<int:investment_log_id>")
def update_new_investment(investment_log_id):
    db: Session = next(get_db())
    investment_log = db.query(InvestmentLog).filter(InvestmentLog.id == investment_log_id).first()
    if not investment_log:
        return Response._error(_("SAVING_NOT_FOUND"),_("NONE"), 404)
    try:
        new_investment_data = InvestmentLogUpdate(**request.json)
    except ValidationError as e:
        return Response._error(_("VALIDATION_ERROR"), e.errors(),400)

    validated_data = new_investment_data.model_dump(exclude_unset=True)
    for key, value in validated_data.items():
        setattr(investment_log, key, value)
    db.commit()
    db.refresh(investment_log)
    return Response._ok_data(InvestmentLogRead.model_validate(investment_log).model_dump(),_("QUERY_OK"), 201)

@router.delete("/investments_logs/<int:investment_log_id>")
def delete_new_investment(investment_log_id):
    db: Session = next(get_db())
    investment_log = db.query(InvestmentLog).filter(InvestmentLog.id == investment_log_id).first()
    if not investment_log:
        return Response._error(("SAVING_NOT_FOUND"),_("NONE"), 404)
    db.delete(investment_log)
    db.commit()
    return Response._error(_("SAVING_DELETED"),_("NONE"), 204)

@router.get("/investments_logs")
def list_investments_logs():
    db: Session = next(get_db())
    investments_logs = db.query(InvestmentLog).all()
    new_investment_data = [InvestmentLogRead.model_validate(u).model_dump() for u in investments_logs]
    if not new_investment_data:
        return Response._error(_("SAVING_NOT_FOUND"),_("NONE"), 404)
    return Response._ok_data(new_investment_data, _("QUERY_OK"), 200)
