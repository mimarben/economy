from fastapi import APIRouter, Body, Depends, Query, Request
from typing import Any
from sqlalchemy.orm import Session
from db.database import get_db
from services.ai.transaction_ai_service import TransactionAIService
from services.core.response_service import Response
from utils.i18n import _

router = APIRouter()
name = "transactions_ai"


@router.post("/transactions/classify")
def classify(payload: dict, db: Session = Depends(get_db)):

    try:
        data = payload or {}

        print(f"Received data for classification: {data}")

        transactions = data.get("transactions", [])
        rules = data.get("rules", [])

        service = TransactionAIService(db)

        result = service.classify(transactions, rules)

        return Response.ok_data(result, _("CLASSIFIED"), 200, name)

    except Exception as e:
        return Response.error(_("AI_ERROR"), str(e), 500, name)
