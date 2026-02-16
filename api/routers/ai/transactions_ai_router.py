from flask import Blueprint, request
from sqlalchemy.orm import Session
from db.database import get_db
from services.ai.transaction_ai_service import TransactionAIService
from services.core.response_service import Response
from flask_babel import _

router = Blueprint("transactions_ai", __name__)
name = "transactions_ai"


@router.post("/transactions/classify")
def classify():

    db: Session = next(get_db())

    try:
        data = request.get_json(force=True)
        print(f"Received data for classification: {data}")
        service = TransactionAIService(db)
        result = service.classify(data)

        return Response._ok_data(result, _("CLASSIFIED"), 200, name)

    except Exception as e:
        return Response._error(_("AI_ERROR"), str(e), 500, name)
