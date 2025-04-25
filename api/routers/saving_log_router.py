from flask import Blueprint, request, jsonify, abort
from sqlalchemy.orm import Session
from pydantic import ValidationError
from flask_babel import _
from services.response_service import Response

from models.models import SavingLog
from schemas.saving_log_schema import SavingLogCreate, SavingLogRead, SavingLogUpdate
from db.database import get_db

router = Blueprint('savings_logs', __name__)
name= "savings_logs"
@router.post("/savings_logs")
def create_new_investment():
    db: Session = next(get_db())
    try:
        new_investment_data = SavingLogCreate.model_validate(request.json, context={"db": db})
    except ValidationError as e:
        return Response._error(_("FK_ERROR_ADD_DATA"),e.errors(), 400, name)
    new_investment_log = SavingLog(**new_investment_data.model_dump())
    db.add(new_investment_log)
    db.commit()
    db.refresh(new_investment_log)
    return Response._ok_data(SavingLogRead.model_validate(new_investment_log).model_dump(),_("SAVING_LOG_CREATED"),201, name)

@router.get("/savings_logs/<int:saving_log_id>")
def get_new_investment(saving_log_id):
    db: Session = next(get_db())
    saving = db.query(SavingLog).filter(SavingLog.id == saving_log_id).first()
    if not saving:
        return Response._error(_("SAVING_LOG_NOT_FOUND"),_("NONE"), 404, name)
    return Response._ok_data(SavingLogRead.model_validate(saving).model_dump(),_("SAVING_LOG_FOUND"),200, name)

@router.patch("/savings_logs/<int:saving_log_id>")
def update_new_investment(saving_log_id):
    db: Session = next(get_db())
    saving = db.query(SavingLog).filter(SavingLog.id == saving_log_id).first()
    if not saving:
        return Response._error(_("SAVING_LOG_NOT_FOUND"),_("NONE"), 404, name)
    try:
        new_investment_data = SavingLogUpdate(**request.json)
    except ValidationError as e:
        return Response._error(_("VALIDATION_ERROR"), e.errors(),400, name)

    validated_data = new_investment_data.model_dump(exclude_unset=True)
    for key, value in validated_data.items():
        setattr(saving, key, value)
    db.commit()
    db.refresh(saving)
    return Response._ok_data(SavingLogRead.model_validate(saving).model_dump(),_("SAVING_LOG_UPDATED"),201, name)

@router.delete("/savings_logs/<int:saving_log_id>")
def delete_new_investment(saving_log_id):
    db: Session = next(get_db())
    saving = db.query(SavingLog).filter(SavingLog.id == saving_log_id).first()
    if not saving:
        return Response._error(("SAVING_LOG_NOT_FOUND"),_("NONE"), 404, name)
    db.delete(saving)
    db.commit()
    return Response._error(_("SAVING_LOG_DELETED"),_("NONE"), 204, name)

@router.get("/savings_logs")
def list_savings_logs():
    db: Session = next(get_db())
    savings_logs = db.query(SavingLog).all()
    new_investment_data = [SavingLogRead.model_validate(u).model_dump() for u in savings_logs]
    if not new_investment_data:
        return Response._error(_("SAVING_LOGS_NOT_FOUND"),_("NONE"), 404,name)
    return Response._ok_data(new_investment_data,_("SAVING_LOGS_FOUND"), 202, name)
