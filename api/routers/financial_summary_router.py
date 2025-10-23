from flask import Blueprint, request, jsonify, abort
from sqlalchemy.orm import Session
from pydantic import ValidationError
from flask_babel import _

from models.models import FinancialSummary
from schemas.financial_summary_schema import FinancialSummaryCreate, FinancialSummaryRead, FinancialSummaryUpdate
from db.database import get_db
from services.response_service import Response


router = Blueprint('financials_summaries', __name__)
name="financials_summaries"
@router.post("/financials_summaries")
def create_financial_summary():
    db: Session = next(get_db())
    try:
        financial_summary_data = FinancialSummaryCreate.model_validate(request.json, context={"db": db})
    except ValidationError as e:
        return Response._error(_("FK_ERROR_ADD_DATA"),e.errors(), 400, name)
    new_financial_summary = FinancialSummary(**financial_summary_data.model_dump())
    db.add(new_financial_summary)
    db.commit()
    db.refresh(new_financial_summary)
    return Response._ok_data(FinancialSummaryRead.model_validate(new_financial_summary).model_dump(),_("FINANCIAL_SUMMARY_CREATED") ,201, name)

@router.get("/financials_summaries/<int:financial_summary_id>")
def get_financial_summary(financial_summary_id):
    db: Session = next(get_db())
    financial_summary = db.query(FinancialSummary).filter(FinancialSummary.id == financial_summary_id).first()
    if not financial_summary:
        return Response._error(_("FINANCIAL_SUMMARY_NOT_FOUND"), _("NONE"), 404, name)
    return Response._ok_data(FinancialSummaryRead.model_validate(financial_summary).model_dump(),_("FINANCIAL_SUMMARY_FOUND"), 200, name)

@router.patch("/financials_summaries/<int:financial_summary_id>")
def update_financial_summary(financial_summary_id):
    db: Session = next(get_db())
    financial_summary = db.query(FinancialSummary).filter(FinancialSummary.id == financial_summary_id).first()
    if not financial_summary:
        return Response._error(_("FINANCIAL_SUMMARY_NOT_FOUND"),_("NONE"), 404, name)

    try:
        financial_summary_data = FinancialSummaryUpdate(**request.json)
    except ValidationError as e:
        return Response._error(_("VALIDATION_ERROR"), e.errors(),400, name)

    validated_data = financial_summary_data.model_dump(exclude_unset=True)
    for key, value in validated_data.items():
        setattr(financial_summary, key, value)

    db.commit()
    db.refresh(financial_summary)
    return Response._ok_data(FinancialSummaryRead.model_validate(financial_summary).model_dump(),_("FINANCIAL_SUMMARY_UPDATED"), 200, name)

@router.delete("/financials_summaries/<int:financial_summary_id>")
def delete_financial_summary(financial_summary_id):
    db: Session = next(get_db())
    financial_summary = db.query(FinancialSummary).filter(FinancialSummary.id == financial_summary_id).first()
    if not financial_summary:
        return Response._error(("FINANCIAL_SUMMARY_NOT_FOUND"),_("NONE"), 404, name)
    db.delete(financial_summary)
    db.commit()
    return Response._error(_("FINANCIAL_SUMMARY_DELETED"),_("NONE"), 204, name)

@router.get("/financials_summaries")
def list_financials_summaries():
    db: Session = next(get_db())
    financials_summaries = db.query(FinancialSummary).all()
    financial_summary_data = [FinancialSummaryRead.model_validate(u).model_dump() for u in financials_summaries]
    if not financial_summary_data:
        return Response._error(_("FINANCIALS_SUMMARIES_NOT_FOUND"),_("NONE"), 404, name)
    return Response._ok_data(financial_summary_data, _("FINANCIALS_SUMMARIES_FOUND"), 200, name)
