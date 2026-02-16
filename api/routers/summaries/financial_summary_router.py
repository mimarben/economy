"""Router for FinancialSummary endpoints following ISP."""
from flask import Blueprint, request
from sqlalchemy.orm import Session
from pydantic import ValidationError
from flask_babel import _

from schemas.summaries.financial_summary_schema import FinancialSummaryCreate, FinancialSummaryUpdate
from services.summaries.financial_summary_service import FinancialSummaryService
from services.core.interfaces import IReadService, ICreateService, IUpdateService, IDeleteService
from db.database import get_db
from services.core.response_service import Response


router = Blueprint("financial_summaries", __name__)
name = "financial_summaries"


def _get_create_service(db: Session) -> ICreateService:
    return FinancialSummaryService(db)


def _get_read_service(db: Session) -> IReadService:
    return FinancialSummaryService(db)


def _get_update_service(db: Session) -> IUpdateService:
    return FinancialSummaryService(db)


def _get_delete_service(db: Session) -> IDeleteService:
    return FinancialSummaryService(db)


@router.post("/financial_summaries")
def create():
    db: Session = next(get_db())
    try:
        data = FinancialSummaryCreate.model_validate(request.json)
    except ValidationError as e:
        return Response._error(_("VALIDATION_ERROR"), e.errors(), 400, name)
    try:
        service: ICreateService = _get_create_service(db)
        result = service.create(data)
        return Response._ok_data(result.model_dump(), _("FINANCIAL_SUMMARY_CREATED"), 201, name)
    except Exception as e:
        return Response._error(_("DATABASE_ERROR"), str(e), 500, name)


@router.get("/financial_summaries/<int:id>")
def get_by_id(id):
    db: Session = next(get_db())
    service: IReadService = _get_read_service(db)
    result = service.get_by_id(id)
    if not result:
        return Response._error(_("FINANCIAL_SUMMARY_NOT_FOUND"), _("NONE"), 404, name)
    return Response._ok_data(result.model_dump(), _("FINANCIAL_SUMMARY_FOUND"), 200, name)


@router.get("/financial_summaries")
def list_all():
    db: Session = next(get_db())
    service: IReadService = _get_read_service(db)
    results = service.get_all()
    return Response._ok_data([r.model_dump() for r in results], _("FINANCIAL_SUMMARY_LIST"), 200, name)


@router.patch("/financial_summaries/<int:id>")
def update(id):
    db: Session = next(get_db())
    try:
        data = FinancialSummaryUpdate.model_validate(request.json)
    except ValidationError as e:
        return Response._error(_("VALIDATION_ERROR"), e.errors(), 400, name)
    try:
        service: IUpdateService = _get_update_service(db)
        result = service.update(id, data)
        if not result:
            return Response._error(_("FINANCIAL_SUMMARY_NOT_FOUND"), _("NONE"), 404, name)
        return Response._ok_data(result.model_dump(), _("FINANCIAL_SUMMARY_UPDATED"), 200, name)
    except Exception as e:
        return Response._error(_("DATABASE_ERROR"), str(e), 500, name)


@router.delete("/financial_summaries/<int:id>")
def delete(id):
    db: Session = next(get_db())
    try:
        service: IDeleteService = _get_delete_service(db)
        success = service.delete(id)
        if not success:
            return Response._error(_("FINANCIAL_SUMMARY_NOT_FOUND"), _("NONE"), 404, name)
        return Response._ok_message(_("FINANCIAL_SUMMARY_DELETED"), 204, name)
    except Exception as e:
        return Response._error(_("DATABASE_ERROR"), str(e), 500, name)
