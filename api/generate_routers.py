#!/usr/bin/env python3
"""Generate refactored routers following ISP pattern."""

ROUTER_TEMPLATE = '''"""Router for {entity_name} endpoints following ISP."""
from flask import Blueprint, request
from sqlalchemy.orm import Session
from pydantic import ValidationError
from flask_babel import _

from schemas.{singular}_schema import {entity_class}Create, {entity_class}Update
from services.{singular}_service import {entity_class}Service
from services.interfaces import IReadService, ICreateService, IUpdateService, IDeleteService
from db.database import get_db
from services.response_service import Response


router = Blueprint("{plural}", __name__)
name = "{plural}"


def _get_create_service(db: Session) -> ICreateService:
    return {entity_class}Service(db)


def _get_read_service(db: Session) -> IReadService:
    return {entity_class}Service(db)


def _get_update_service(db: Session) -> IUpdateService:
    return {entity_class}Service(db)


def _get_delete_service(db: Session) -> IDeleteService:
    return {entity_class}Service(db)


@router.post("/{plural}")
def create():
    db: Session = next(get_db())
    try:
        data = {entity_class}Create.model_validate(request.json)
    except ValidationError as e:
        return Response._error(_("VALIDATION_ERROR"), e.errors(), 400, name)
    try:
        service: ICreateService = _get_create_service(db)
        result = service.create(data)
        return Response._ok_data(result.model_dump(), _("{upper}_CREATED"), 201, name)
    except ValueError as e:
        return Response._error(_("INVALID_DATA"), str(e), 400, name)
    except Exception as e:
        return Response._error(_("DATABASE_ERROR"), str(e), 500, name)


@router.get("/{plural}/<int:id>")
def get_by_id(id):
    db: Session = next(get_db())
    try:
        service: IReadService = _get_read_service(db)
        result = service.get_by_id(id)
        if not result:
            return Response._error(_("{upper}_NOT_FOUND"), _("NONE"), 404, name)
        return Response._ok_data(result.model_dump(), _("{upper}_FOUND"), 200, name)
    except Exception as e:
        return Response._error(_("DATABASE_ERROR"), str(e), 500, name)


@router.get("/{plural}")
def list_all():
    db: Session = next(get_db())
    try:
        service: IReadService = _get_read_service(db)
        results = service.get_all()
        return Response._ok_data([r.model_dump() for r in results], _("{upper}_LIST"), 200, name)
    except Exception as e:
        return Response._error(_("DATABASE_ERROR"), str(e), 500, name)


@router.patch("/{plural}/<int:id>")
def update(id):
    db: Session = next(get_db())
    try:
        data = {entity_class}Update.model_validate(request.json)
    except ValidationError as e:
        return Response._error(_("VALIDATION_ERROR"), e.errors(), 400, name)
    try:
        service: IUpdateService = _get_update_service(db)
        result = service.update(id, data)
        if not result:
            return Response._error(_("{upper}_NOT_FOUND"), _("NONE"), 404, name)
        return Response._ok_data(result.model_dump(), _("{upper}_UPDATED"), 200, name)
    except Exception as e:
        return Response._error(_("DATABASE_ERROR"), str(e), 500, name)


@router.delete("/{plural}/<int:id>")
def delete(id):
    db: Session = next(get_db())
    try:
        service: IDeleteService = _get_delete_service(db)
        success = service.delete(id)
        if not success:
            return Response._error(_("{upper}_NOT_FOUND"), _("NONE"), 404, name)
        return Response._ok_message(_("{upper}_DELETED"), 204, name)
    except Exception as e:
        return Response._error(_("DATABASE_ERROR"), str(e), 500, name)
'''

ROUTERS = [
    {"class": "ExpensesCategory", "name": "expenses_categories", "singular": "expense_category", "plural": "expenses_categories"},
    {"class": "IncomesCategory", "name": "income_categories", "singular": "income_category", "plural": "income_categories"},
    {"class": "Income", "name": "incomes", "singular": "income", "plural": "incomes"},
    {"class": "Saving", "name": "savings", "singular": "saving", "plural": "savings"},
    {"class": "SavingLog", "name": "saving_logs", "singular": "saving_log", "plural": "saving_logs"},
    {"class": "InvestmentsCategory", "name": "investment_categories", "singular": "investment_category", "plural": "investment_categories"},
    {"class": "Investment", "name": "investments", "singular": "investment", "plural": "investments"},
    {"class": "InvestmentLog", "name": "investment_logs", "singular": "investment_log", "plural": "investment_logs"},
    {"class": "FinancialSummary", "name": "financial_summaries", "singular": "financial_summary", "plural": "financial_summaries"},
    {"class": "Household", "name": "households", "singular": "household", "plural": "households"},
    {"class": "HouseholdMember", "name": "household_members", "singular": "household_member", "plural": "household_members"},
    {"class": "Source", "name": "sources", "singular": "source", "plural": "sources"},
]

def generate():
    for router in ROUTERS:
        code = ROUTER_TEMPLATE.format(
            entity_class=router["class"],
            entity_name=router["name"],
            singular=router["singular"],
            plural=router["plural"],
            upper=router["singular"].upper(),
        )
        filename = f"/home/miguel/src/economy/api/routers/{router['singular']}_router.py"
        print(f"# {filename}\n{code}\n\n")

if __name__ == "__main__":
    generate()
