from fastapi import APIRouter, Body, Depends, Query, Request
from typing import Any
from sqlalchemy.orm import Session
from pydantic import ValidationError
from utils.i18n import _

from schemas.imports.import_schema import BulkImportRequest
from services.imports.import_service import ImportService
from db.database import get_db
from services.core.response_service import Response


router = APIRouter()
name = "imports"


@router.post("/imports/transactions/bulk")
def import_transactions_bulk(payload: BulkImportRequest, db: Session = Depends(get_db)):
    """
    Import multiple expenses and incomes atomically.

    If any item fails format or fk validation, none are persisted.
    """
    try:
        data = BulkImportRequest.model_validate(payload)
    except ValidationError as e:
        return Response.error(_("VALIDATION_ERROR"), e.errors(), 400, name)

    try:
        service = ImportService(db)
        result = service.import_transactions_atomic(data)
        return Response.ok_data(
            result,
            _("TRANSACTIONS_IMPORTED"),
            201,
            name
        )
    except ValueError as e:
        return Response.error(_("FK_ERROR"), str(e), 400, name)
    except Exception as e:
        db.rollback()
        return Response.error(_("DATABASE_ERROR"), str(e), 500, name)
